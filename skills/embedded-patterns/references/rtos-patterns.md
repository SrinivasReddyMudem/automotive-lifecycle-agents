# RTOS Patterns for Automotive Embedded SW

Five common RTOS patterns with structure, pitfalls, and safety/MISRA notes.
All code examples use synthetic patterns — no real project code.

---

## Pattern 1 — Producer-Consumer via Message Queue

**Use case:** ISR or fast task sends data to a slower processing task.

**Structure:**
```c
/* Queue handle — created at init, never during runtime */
static QueueHandle_t g_speed_queue;

/* ISR or high-prio task: producer */
void CAN_SpeedRxCallback(uint16_t raw_speed) {
    BaseType_t higher_prio_woken = pdFALSE;
    (void)xQueueSendFromISR(g_speed_queue, &raw_speed, &higher_prio_woken);
    portYIELD_FROM_ISR(higher_prio_woken);
}

/* Low-priority task: consumer */
void SpeedProcessingTask(void *params) {
    uint16_t raw_speed = 0U;
    for (;;) {
        if (xQueueReceive(g_speed_queue, &raw_speed, portMAX_DELAY) == pdTRUE) {
            /* process speed — no time pressure here */
        }
    }
}
```

**Pitfalls:** Queue overflow if producer is faster than consumer; size queue for worst-case burst.
**MISRA note:** `BaseType_t` is platform-specific — document in portability section.
**Safety note:** Queue creation must succeed before any task is started; check return value.

---

## Pattern 2 — Periodic Task with Deadline Monitoring

**Use case:** AUTOSAR-like cyclic runnable; ECU main function cycle.

**Structure:**
```c
#define TASK_PERIOD_MS    (10U)
#define DEADLINE_SLACK_MS (2U)

void VehicleControl_10ms_Task(void *params) {
    TickType_t last_wake = xTaskGetTickCount();
    for (;;) {
        /* Deadline check: measure actual execution time */
        TickType_t start = xTaskGetTickCount();
        VehicleControl_MainFunction();
        TickType_t exec_time = xTaskGetTickCount() - start;

        if (exec_time > pdMS_TO_TICKS(TASK_PERIOD_MS - DEADLINE_SLACK_MS)) {
            Dem_ReportErrorStatus(DEM_DEADLINE_EXCEEDED, DEM_EVENT_STATUS_FAILED);
        }

        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(TASK_PERIOD_MS));
    }
}
```

**Pitfalls:** `vTaskDelayUntil` drifts if task overruns; log overruns for analysis.
**MISRA note:** Cast tick differences to appropriate type to avoid implicit narrowing.
**Safety note:** Deadline monitoring is a safety mechanism for ASIL-B and above.

---

## Pattern 3 — Mutex-Protected Shared Resource

**Use case:** Multiple tasks access shared data (e.g., NvM buffer, calibration values).

**Structure:**
```c
static SemaphoreHandle_t g_calib_mutex;
static CalibData_T       g_calib_data;

/* Accessor — always use this, never access g_calib_data directly */
Std_ReturnType Calib_GetSpeed(uint16_t *speed_out) {
    Std_ReturnType ret = E_NOT_OK;
    if (xSemaphoreTake(g_calib_mutex, pdMS_TO_TICKS(5U)) == pdTRUE) {
        *speed_out = g_calib_data.speed_limit;
        (void)xSemaphoreGive(g_calib_mutex);
        ret = E_OK;
    }
    return ret;
}
```

**Pitfalls:** Never hold mutex in ISR — use a queue or flag instead.
**MISRA note:** Always check semaphore return value; don't assume success.
**Safety note:** Use mutex with priority inheritance to prevent priority inversion.

---

## Pattern 4 — Watchdog Service Pattern

**Use case:** Ensuring all critical tasks check in; system reset if a task hangs.

**Structure:**
```c
#define WDG_TASK_A_BIT   (0x01U)
#define WDG_TASK_B_BIT   (0x02U)
#define WDG_ALL_BITS     (WDG_TASK_A_BIT | WDG_TASK_B_BIT)

static volatile uint8_t g_wdg_checkin = 0U;

/* Called by each task at each cycle */
void Wdg_CheckIn(uint8_t task_bit) {
    uint8_t current = __atomic_fetch_or(&g_wdg_checkin, task_bit, __ATOMIC_SEQ_CST);
    (void)current;
}

/* Watchdog monitor task — highest priority */
void WdgMonitor_Task(void *params) {
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(20U));
        if ((g_wdg_checkin & WDG_ALL_BITS) == WDG_ALL_BITS) {
            g_wdg_checkin = 0U;
            Wdg_HwService();  /* hardware watchdog kick */
        } else {
            /* task missing — do NOT service watchdog → system reset */
            Dem_ReportErrorStatus(DEM_WDG_TASK_MISS, DEM_EVENT_STATUS_FAILED);
        }
    }
}
```

**Pitfalls:** Watchdog monitor must have highest priority; never starved.
**MISRA note:** Atomic operations on shared byte require appropriate intrinsics.
**Safety note:** This pattern is a safety mechanism — it must be MISRA-compliant.

---

## Pattern 5 — Software Timer for Non-Blocking Delays

**Use case:** Debounce, timeout detection, LED blink — without blocking or RTOS tasks.

**Structure:**
```c
typedef struct {
    uint32_t start_tick;
    uint32_t period_ms;
    boolean  running;
} SwTimer_T;

void SwTimer_Start(SwTimer_T *timer, uint32_t period_ms) {
    timer->start_tick = GetSystemTick_ms();  /* platform function */
    timer->period_ms  = period_ms;
    timer->running    = TRUE;
}

boolean SwTimer_Elapsed(const SwTimer_T *timer) {
    boolean elapsed = FALSE;
    if (timer->running) {
        uint32_t now  = GetSystemTick_ms();
        uint32_t diff = now - timer->start_tick;  /* wraps correctly */
        elapsed = (diff >= timer->period_ms);
    }
    return elapsed;
}
```

**Pitfalls:** Tick subtraction handles wraparound correctly only for uint types.
**MISRA note:** Use unsigned types for tick values to ensure subtraction is defined.
**Safety note:** This is preferred over `while (tick < target)` which is a busy-wait.
