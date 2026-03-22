# AUTOSAR Classic OS and COM API Reference

## AUTOSAR OS API (OSEK/ISO 17356)

### Task Management

```c
/* Activate a task — puts it into READY state */
StatusType ActivateTask(TaskType TaskID);
/* Returns: E_OK, E_OS_ID (invalid), E_OS_LIMIT (too many activations) */

/* Terminate calling task — must be last statement in task body */
StatusType TerminateTask(void);
/* Returns: E_OK (never returned), E_OS_RESOURCE (resource still held) */

/* Terminate and chain to successor task (atomic) */
StatusType ChainTask(TaskType TaskID);

/* Force rescheduling — for non-preemptive tasks */
StatusType Schedule(void);

/* Get current running task ID */
StatusType GetTaskID(TaskRefType TaskID);

/* Get state of any task: RUNNING, READY, WAITING, SUSPENDED */
StatusType GetTaskState(TaskType TaskID, TaskStateRefType State);
```

### Event Management (Extended Tasks Only)

```c
/* Set events on a task (wakes it from WaitEvent) */
StatusType SetEvent(TaskType TaskID, EventMaskType Mask);
/* Returns: E_OS_ACCESS (task not extended), E_OS_STATE (task suspended) */

/* Clear events on calling task */
StatusType ClearEvent(EventMaskType Mask);

/* Read current event state */
StatusType GetEvent(TaskType TaskID, EventMaskRefType Event);

/* Block calling task until events occur */
StatusType WaitEvent(EventMaskType Mask);
/* Returns: E_OS_RESOURCE (resource held — cannot block) */
```

**Typical usage pattern:**
```c
TASK(Task_10ms) {
    EventMaskType events;
    while (1) {
        WaitEvent(EVENT_NEW_DATA | EVENT_TIMER);
        GetEvent(MYTASK, &events);

        if (events & EVENT_NEW_DATA) {
            ClearEvent(EVENT_NEW_DATA);
            ProcessNewData();
        }
        if (events & EVENT_TIMER) {
            ClearEvent(EVENT_TIMER);
            RunPeriodicFunction();
        }
    }
}
```

### Resource Management (Priority Ceiling Protocol)

```c
/* Occupy resource — raises task priority to ceiling */
StatusType GetResource(ResourceType ResID);

/* Release resource — restores previous priority */
StatusType ReleaseResource(ResourceType ResID);
```

**Rules**:
- Resources MUST be released in reverse order of acquisition (LIFO)
- Cannot call WaitEvent while holding a resource
- RES_SCHEDULER is a special internal resource for non-preemptive sections

### Alarm Management

```c
/* Get alarm base info (min cycle, max value, ticks per base) */
StatusType GetAlarmBase(AlarmType AlarmID, AlarmBaseRefType Info);

/* Get remaining ticks until alarm fires */
StatusType GetAlarm(AlarmType AlarmID, TickRefType Tick);

/* Set relative alarm (fires after Increment ticks, repeats every Cycle) */
StatusType SetRelAlarm(AlarmType AlarmID, TickType Increment, TickType Cycle);
/* Cycle=0: single-shot alarm. Cycle>0: cyclic alarm. */

/* Set absolute alarm (fires at Start tick value) */
StatusType SetAbsAlarm(AlarmType AlarmID, TickType Start, TickType Cycle);

/* Cancel alarm */
StatusType CancelAlarm(AlarmType AlarmID);
```

**Typical alarm setup (done once at startup):**
```c
/* Activate Task_10ms every 10 ticks (10ms if 1 tick = 1ms) */
SetRelAlarm(ALARM_10MS, 10, 10);

/* Alarm action defined in OIL: ACTIVATETASK or SETEVENT or ALARMCALLBACK */
```

### Schedule Table Management

```c
/* Start schedule table relative to current counter value */
StatusType StartScheduleTableRel(ScheduleTableType SchedTabID, TickType Offset);

/* Start at absolute counter value */
StatusType StartScheduleTableAbs(ScheduleTableType SchedTabID, TickType Start);

/* Stop schedule table */
StatusType StopScheduleTable(ScheduleTableType SchedTabID);

/* Switch to next schedule table at current table's wrap point */
StatusType NextScheduleTable(ScheduleTableType From, ScheduleTableType To);

/* Get current status: STOPPED, RUNNING, RUNNING_AND_SYNCHRONOUS, WAITING, NEXT */
StatusType GetScheduleTableStatus(ScheduleTableType SchedTabID,
                                   ScheduleTableStatusRefType Status);
```

### OS Status Types

```c
#define E_OK                    0   /* No error */
#define E_OS_ACCESS             1   /* Insufficient rights */
#define E_OS_CALLEVEL           2   /* Called from wrong context (e.g. ISR Cat 1) */
#define E_OS_ID                 3   /* Invalid ID */
#define E_OS_LIMIT              4   /* Limit exceeded */
#define E_OS_NOFUNC             5   /* Function not applicable (e.g. cancel inactive alarm) */
#define E_OS_RESOURCE           6   /* Resource still held */
#define E_OS_STATE              7   /* Object in wrong state */
#define E_OS_VALUE              8   /* Parameter out of range */
#define E_OS_STACKFAULT         13  /* Stack overflow detected */
#define E_OS_PROTECTION_MEMORY  14  /* MPU protection violation */
#define E_OS_PROTECTION_TIME    15  /* Timing protection violation */
```

---

## OIL Configuration Examples

### Task with Timing Protection (ASIL D)

```oil
TASK Task_10ms {
    PRIORITY = 10;
    SCHEDULE = FULL;           /* Preemptive */
    ACTIVATION = 1;
    AUTOSTART = FALSE;
    STACKSIZE = 1024;
    TYPE = EXTENDED;           /* Can call WaitEvent */
    EVENT = Event_DataReady;
    RESOURCE = ResourceCAN;

    TIMING_PROTECTION = TRUE {
        EXECUTIONBUDGET = 5.0;       /* Max 5ms execution time */
        TIMELIMIT = 10.0;            /* Max 10ms between start and finish */
        RESOURCELOCKLIMIT = 1.0;     /* Max 1ms holding ResourceCAN */
    };
};

TASK Task_100ms {
    PRIORITY = 5;
    SCHEDULE = NON;            /* Non-preemptive — used for QM partition */
    ACTIVATION = 2;            /* Queue depth 2 */
    AUTOSTART = FALSE;
    STACKSIZE = 2048;
    TYPE = BASIC;
};
```

### ISR Definitions

```oil
/* Category 1: No OS services allowed, minimal latency */
ISR ISR_TimerOverflow {
    CATEGORY = 1;
    PRIORITY = 20;
};

/* Category 2: OS services allowed (ActivateTask, SetEvent, etc.) */
ISR ISR_CANReceive {
    CATEGORY = 2;
    PRIORITY = 15;
    RESOURCE = ResourceCAN;
    STACKSIZE = 256;
};
```

### Counter and Alarm Configuration

```oil
COUNTER SystemCounter {
    MINCYCLE = 1;
    MAXALLOWEDVALUE = 65535;
    TICKSPERBASE = 1;
    TYPE = HARDWARE;
    UNIT = TICKS;
    SOURCE = GPT_CHANNEL_0;
};

ALARM Alarm_10ms {
    COUNTER = SystemCounter;
    ACTION = ACTIVATETASK { TASK = Task_10ms; };
    AUTOSTART = TRUE {
        APPMODE = AppMode1;
        ALARMTIME = 10;     /* First fire at tick 10 */
        CYCLETIME = 10;     /* Then every 10 ticks */
    };
};

ALARM Alarm_DataReady {
    COUNTER = SystemCounter;
    ACTION = SETEVENT {
        TASK = Task_10ms;
        EVENT = Event_DataReady;
    };
    AUTOSTART = FALSE;      /* Started programmatically */
};
```

### OS Application (Memory/Temporal Partition)

```oil
APPLICATION App_Powertrain {
    TRUSTED = TRUE;           /* Can access all memory */
    STARTUPHOOK = TRUE;
    SHUTDOWNHOOK = TRUE;
    ERRORHOOK = TRUE;
    HAS_RESTARTTASK = TRUE;

    TASK = Task_10ms;
    TASK = Task_100ms;
    ISR = ISR_CANReceive;
    COUNTER = SystemCounter;
    ALARM = Alarm_10ms;
    RESOURCE = ResourceCAN;
    TIMING_PROTECTION = TRUE;
};

APPLICATION App_Infotainment {
    TRUSTED = FALSE;          /* No access to App_Powertrain memory */
    STARTUPHOOK = FALSE;
    SHUTDOWNHOOK = FALSE;
    ERRORHOOK = FALSE;
};
```

---

## COM Module API (AUTOSAR R4/R22)

### Signal Transmission and Reception

```c
/* Initialize COM module */
void Com_Init(const Com_ConfigType* config);
void Com_DeInit(void);

/* Enable/disable I-PDU group */
void Com_IpduGroupControl(Com_IpduGroupIdType ipduGroupId, boolean initialize);

/* Send signal — called from application SWC */
uint8 Com_SendSignal(Com_SignalIdType signalId, const void* signalDataPtr);
/* Returns: COM_SERVICE_NOT_AVAILABLE, COM_BUSY, E_OK */

/* Receive signal — called from application SWC */
uint8 Com_ReceiveSignal(Com_SignalIdType signalId, void* signalDataPtr);
/* Returns: COM_SERVICE_NOT_AVAILABLE, COM_NEVER_RECEIVED, E_OK */

/* Trigger immediate I-PDU send (bypass cycle timer) */
Std_ReturnType Com_TriggerIPDUSend(PduIdType pduId);

/* Main function for periodic Rx/Tx processing — called by OS task */
void Com_MainFunctionRx(void);
void Com_MainFunctionTx(void);
void Com_MainFunctionRouteSignals(void);
```

### Signal Group API

```c
/* Lock signal group shadow buffer, then send all at once */
uint8 Com_SendSignalGroup(Com_SignalGroupIdType signalGroupId);

/* Receive signal group — reads snapshot */
uint8 Com_ReceiveSignalGroup(Com_SignalGroupIdType signalGroupId);

/* Update individual signal in shadow buffer before SendSignalGroup */
void Com_UpdateShadowSignal(Com_SignalIdType signalId, const void* signalDataPtr);

/* Read individual signal from shadow buffer after ReceiveSignalGroup */
void Com_ReceiveShadowSignal(Com_SignalIdType signalId, void* signalDataPtr);
```

**Correct signal group usage:**
```c
/* Sender side */
Com_UpdateShadowSignal(SIG_SPEED_VALUE, &speedValue);
Com_UpdateShadowSignal(SIG_SPEED_VALID, &speedValid);
Com_SendSignalGroup(SIGGRP_VEHICLE_SPEED);  /* Atomic send */

/* Receiver side */
Com_ReceiveSignalGroup(SIGGRP_VEHICLE_SPEED);  /* Atomic receive */
Com_ReceiveShadowSignal(SIG_SPEED_VALUE, &speedValue);
Com_ReceiveShadowSignal(SIG_SPEED_VALID, &speedValid);
```

---

## NvM Module API

```c
void NvM_Init(const NvM_ConfigType* ConfigPtr);

/* Request read of NV block to RAM mirror */
Std_ReturnType NvM_ReadBlock(NvM_BlockIdType BlockId, void* NvM_DstPtr);

/* Request write of RAM mirror to NV */
Std_ReturnType NvM_WriteBlock(NvM_BlockIdType BlockId, const void* NvM_SrcPtr);

/* Request restore of default values */
Std_ReturnType NvM_RestoreBlockDefaults(NvM_BlockIdType BlockId, void* NvM_DestPtr);

/* Erase a block */
Std_ReturnType NvM_EraseNvBlock(NvM_BlockIdType BlockId);

/* Cancel pending request */
Std_ReturnType NvM_CancelWriteAll(void);

/* Get request result: NVM_REQ_OK, NVM_REQ_PENDING, NVM_REQ_NOT_OK */
Std_ReturnType NvM_GetErrorStatus(NvM_BlockIdType BlockId,
                                   NvM_RequestResultType* RequestResultPtr);

/* Main function — called periodically from OS task */
void NvM_MainFunction(void);
```

**NvM usage pattern (non-blocking):**
```c
/* Start read at init */
NvM_ReadBlock(BLOCK_ODOMETER, &OdometerData);

/* Poll in main loop until complete */
NvM_RequestResultType result;
NvM_GetErrorStatus(BLOCK_ODOMETER, &result);
if (result == NVM_REQ_OK) {
    /* Data is valid */
} else if (result == NVM_REQ_NOT_OK) {
    /* Use default values */
    OdometerData = ODOMETER_DEFAULT;
}
```

---

## DCM (Diagnostic Communication Manager) Callbacks

```c
/* Called when tester enters/exits diagnostic session */
Std_ReturnType Dcm_GetSesCtrlType(Dcm_SesCtrlType* SesCtrlType);

/* Security access seed generation — implement in application */
Std_ReturnType DcmAppl_DcmGetSeed(uint8* SecurityAccessDataRecord,
                                    uint8 SecurityAccessDataRecordSize,
                                    uint8* Seed,
                                    uint16* SeedLen,
                                    Dcm_NegativeResponseCodeType* ErrorCode);

/* Security access key comparison — implement in application */
Std_ReturnType DcmAppl_DcmCompareKey(uint8* Key,
                                       uint16 KeyLen,
                                       Dcm_NegativeResponseCodeType* ErrorCode);

/* Routine control start — implement per routine */
Std_ReturnType DcmAppl_RoutineControlStart(uint16 RoutineIdentifier,
                                             uint8* InBuffer,
                                             uint16 InBufferSize,
                                             uint8* OutBuffer,
                                             uint16* OutBufferSizePtr,
                                             Dcm_NegativeResponseCodeType* ErrorCode);
```

---

## Common AUTOSAR Error Patterns

| Pattern | Root Cause | Fix |
|---------|-----------|-----|
| Task stack overflow | STACKSIZE too small for deepest call chain | Profile with stack painting; increase STACKSIZE |
| E_OS_RESOURCE at TerminateTask | Resource not released before task end | Always release in LIFO order before TerminateTask |
| E_OS_CALLEVEL from ISR Cat 1 | Calling OS service from Cat 1 ISR | Use Cat 2 ISR for any OS service call |
| E_OS_PROTECTION_TIME | Task exceeds EXECUTIONBUDGET | Profile task; reduce runtime or increase budget |
| COM_NEVER_RECEIVED | Signal never received since startup | Check I-PDU group enabled; check sender active |
| NVM_REQ_PENDING forever | NvM_MainFunction not called | Ensure NvM_MainFunction in periodic task |
| Signal value stale | Com_MainFunctionRx not called | Map Com_MainFunctionRx to correct periodic task |
