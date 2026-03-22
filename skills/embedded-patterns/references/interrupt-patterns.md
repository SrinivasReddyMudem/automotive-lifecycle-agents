# Interrupt Patterns for Automotive Embedded SW

Interrupt handler design, volatile usage, shared variable protection,
ISR-to-task communication. All code examples are synthetic.

---

## Rule 1 — Volatile for ISR-shared variables

Any variable written by an ISR and read by another context (main loop, task)
must be declared `volatile`. Without `volatile`, the compiler may cache the
value in a register and never re-read from memory.

**Non-compliant (synthetic):**
```c
static uint8_t g_rx_ready = 0U;  /* missing volatile */

void UART_RxISR(void) {
    g_rx_ready = 1U;  /* compiler may not write to memory */
}

void main_loop(void) {
    while (g_rx_ready == 0U) {}  /* may loop forever — cached register */
}
```

**Compliant:**
```c
static volatile uint8_t g_rx_ready = 0U;

void UART_RxISR(void) {
    g_rx_ready = 1U;
}

void main_loop(void) {
    while (g_rx_ready == 0U) {}  /* always re-reads from memory */
}
```

**MISRA note:** `volatile` does not guarantee atomicity. Use atomic access for
multi-byte variables or types wider than the CPU data bus.

---

## Rule 2 — Atomic flag setting for shared boolean

On 32-bit MCUs, 32-bit aligned reads/writes are typically atomic.
On 8-bit MCUs, multi-byte operations are NOT atomic.
Use a single byte flag where possible; use critical section for wider data.

**Pattern — atomic event flag:**
```c
static volatile uint8_t g_can_rx_flag = 0U;  /* 1 = new frame received */

/* ISR context */
void CAN_RxISR(void) {
    /* Copy data to ring buffer first, then set flag */
    RingBuffer_Write(&g_can_rx_buf, &g_rx_frame);
    g_can_rx_flag = 1U;  /* single-byte write is atomic on most MCUs */
}

/* Task context */
void CAN_ProcessTask(void) {
    if (g_can_rx_flag != 0U) {
        g_can_rx_flag = 0U;  /* clear before processing to avoid race */
        CAN_ProcessFrame(RingBuffer_Read(&g_can_rx_buf));
    }
}
```

---

## Rule 3 — ISR must not block or use blocking APIs

ISRs run with preemption disabled (or at high priority).
A blocking call in an ISR will deadlock or violate timing.

**Forbidden in ISR:**
- `vTaskDelay()` — blocks the ISR
- `xSemaphoreTake()` — can block if semaphore not available
- `printf()` / UART write with timeout — can block waiting for hardware
- `malloc()` / `free()` — heap management is not ISR-safe
- Any NvM or flash operation — slow hardware, non-reentrant

**Allowed in ISR:**
- `xSemaphoreGiveFromISR()` — signals a task, does not block
- `xQueueSendFromISR()` — enqueues data, does not block
- `xTaskNotifyFromISR()` — direct task notification, does not block
- Writing to a volatile ring buffer (carefully, with size guard)

---

## Rule 4 — ISR-to-task ring buffer communication

**Structure (synthetic, MISRA-compatible style):**
```c
#define RING_BUF_SIZE  (16U)

typedef struct {
    uint16_t  data[RING_BUF_SIZE];
    uint8_t   head;  /* write index — modified only by ISR */
    uint8_t   tail;  /* read index — modified only by task */
} RingBuf16_T;

static volatile RingBuf16_T g_can_rx_buf = {0};

/* Called from ISR — head increment is safe (ISR is single writer) */
void RingBuf_WriteISR(volatile RingBuf16_T *buf, uint16_t val) {
    uint8_t next_head = (uint8_t)((buf->head + 1U) % RING_BUF_SIZE);
    if (next_head != buf->tail) {  /* not full */
        buf->data[buf->head] = val;
        buf->head = next_head;
    }
    /* silently drop if full — log overflow count if needed */
}

/* Called from task — tail increment is safe (task is single reader) */
boolean RingBuf_ReadTask(volatile RingBuf16_T *buf, uint16_t *out) {
    boolean available = FALSE;
    if (buf->tail != buf->head) {
        *out = buf->data[buf->tail];
        buf->tail = (uint8_t)((buf->tail + 1U) % RING_BUF_SIZE);
        available = TRUE;
    }
    return available;
}
```

**Key property:** Single-producer single-consumer ring buffer requires no mutex.
Head only modified by ISR; tail only modified by task → no race condition.

---

## Rule 5 — Interrupt priority assignment

| Priority Level | Assigned to                                       | Notes                           |
|----------------|---------------------------------------------------|---------------------------------|
| Highest (1)    | Hardware fault, NMI, watchdog                     | Cannot be masked                |
| High (2–4)     | Time-critical ISRs: CAN Rx, timer, ADC            | Service quickly, signal task    |
| Medium (5–8)   | UART, SPI communication ISRs                      | Tolerate short delay            |
| Low (9–12)     | Slow peripherals: I2C, low-speed sensors           | Can be preempted by higher      |
| Lowest (13–15) | Background processing flags                        | Rarely needed at ISR level      |

**AUTOSAR OS note:** In AUTOSAR OS, interrupt priorities must be configured
in the OS resource ceiling protocol. ISRs that call OS APIs must use
Category 2 interrupts. Never call OS APIs from Category 1 ISRs.

---

## Automotive Ethernet — Interrupt and DMA patterns

Modern ECUs increasingly use Automotive Ethernet (100BASE-T1, 1000BASE-T1).
Key differences from CAN for ISR design:

- **Frame size:** Ethernet frames up to 1522 bytes vs CAN max 8 bytes (64 for CAN-FD)
- **DMA mandatory:** Copying 1522 bytes in ISR is too slow — use DMA + completion ISR
- **TSN time-stamping:** Ethernet TSN requires hardware timestamping in ISR for IEEE 802.1AS
- **SOME/IP:** Application-layer protocol; processed in task context, not ISR

**DMA + completion ISR pattern:**
```c
/* DMA is configured to receive Ethernet frame into static buffer */
static uint8_t g_eth_rx_buf[ETH_MAX_FRAME_SIZE];

/* DMA completion ISR — minimal work, signal task */
void ETH_DMA_RxCompleteISR(void) {
    BaseType_t woken = pdFALSE;
    (void)xSemaphoreGiveFromISR(g_eth_rx_sem, &woken);
    portYIELD_FROM_ISR(woken);
}

/* Ethernet receive task — does real work */
void ETH_RxTask(void *params) {
    for (;;) {
        (void)xSemaphoreTake(g_eth_rx_sem, portMAX_DELAY);
        ETH_ProcessFrame(g_eth_rx_buf);
        ETH_RestartDmaRx();  /* re-arm DMA for next frame */
    }
}
```
