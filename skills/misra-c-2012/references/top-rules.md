# MISRA C:2012 — Top 15 Violated Rules in Automotive Embedded Development

All code examples use synthetic data only.

---

## Rule 1.3 — No undefined or critical unspecified behaviour (Required)

**Full rule text:** There shall be no occurrence of undefined or critical
unspecified behaviour.

**Violation example (synthetic):**
```c
/* Signed integer overflow — undefined behaviour in C */
int16_t rpm = 30000;
rpm = rpm + 10000;  /* MISRA 1.3: overflow is undefined */
```

**Compliant rewrite:**
```c
int16_t rpm = 30000;
if (rpm <= (INT16_MAX - 10000)) {
    rpm = rpm + 10000;
} else {
    rpm = INT16_MAX;  /* saturate */
}
```

**Memory aid:** Any UB in C is unpredictable on real hardware — avoid at all costs.
**AUTOSAR context:** Sensor scaling functions, RPM/speed calculations.

---

## Rule 2.2 — No dead code (Required)

**Full rule text:** There shall be no dead code.

**Violation example (synthetic):**
```c
uint8_t get_status(void) {
    uint8_t result = STATUS_OK;
    return result;
    result = STATUS_ERROR;  /* MISRA 2.2: unreachable */
}
```

**Compliant rewrite:**
```c
uint8_t get_status(void) {
    return STATUS_OK;
}
```

**Memory aid:** Dead code signals logic errors; remove or restructure.
**AUTOSAR context:** Runnable bodies after refactoring, unused error paths.

---

## Rule 8.4 — Compatible declaration for external functions (Required)

**Full rule text:** A compatible declaration shall be visible when an object
or function with external linkage is defined.

**Violation example (synthetic):**
```c
/* In module_a.c — no matching header declaration */
uint8_t Rte_Read_Speed(uint16_t *speed) { ... }  /* MISRA 8.4 */
```

**Compliant rewrite:**
```c
/* In module_a.h */
extern uint8_t Rte_Read_Speed(uint16_t *speed);

/* In module_a.c */
#include "module_a.h"
uint8_t Rte_Read_Speed(uint16_t *speed) { ... }
```

**Memory aid:** Always include the header in the translation unit that defines the function.
**AUTOSAR context:** RTE API implementations, BSW callback functions.

---

## Rule 10.1 — Inappropriate essential type for operands (Required)

**Full rule text:** Operands shall not be of an inappropriate essential type.

**Violation example (synthetic):**
```c
uint8_t flags = 0xAAU;
uint8_t result = flags << 8U;  /* MISRA 10.1: shifting 8-bit type by 8 */
```

**Compliant rewrite:**
```c
uint8_t flags = 0xAAU;
uint16_t result = (uint16_t)((uint16_t)flags << 8U);
```

**Memory aid:** Widen operands before shifting or arithmetic that can overflow.
**AUTOSAR context:** CAN signal packing, bit manipulation in ComStack.

---

## Rule 10.3 — Assignment to different essential type (Required)

**Full rule text:** The value of an expression shall not be assigned to an
object with a narrower essential type or of a different essential type category.

**Violation example (synthetic):**
```c
uint16_t speed_raw = 1500U;
uint8_t speed_byte = speed_raw;  /* MISRA 10.3: narrowing implicit conversion */
```

**Compliant rewrite:**
```c
uint16_t speed_raw = 1500U;
uint8_t speed_byte = (uint8_t)(speed_raw & 0x00FFU);  /* explicit cast + mask */
```

**Memory aid:** Explicit cast = documented intent; no cast = hidden data loss.
**AUTOSAR context:** Signal range compression, NvM storage of scaled values.

---

## Rule 11.3 — No cast between pointer to object types (Required)

**Full rule text:** A cast shall not be performed between a pointer to object
type and a pointer to a different object type.

**Violation example (synthetic):**
```c
uint32_t reg_val = 0xDEADBEEFU;
uint8_t *byte_ptr = (uint8_t *)&reg_val;  /* MISRA 11.3 */
```

**Compliant rewrite:**
```c
/* Use a union for type-punning — requires deviation or architecture review */
/* Or restructure to avoid needing raw pointer access */
uint32_t reg_val = 0xDEADBEEFU;
uint8_t byte0 = (uint8_t)(reg_val & 0xFFU);
uint8_t byte1 = (uint8_t)((reg_val >> 8U) & 0xFFU);
```

**Memory aid:** Pointer casts hide alignment and endian bugs — use explicit extraction.
**AUTOSAR context:** Serialisation of PDU buffers, memory-mapped register access.

---

## Rule 11.5 — No cast from void pointer to object pointer (Advisory)

**Full rule text:** A conversion shall not be performed from pointer to void
into pointer to object.

**Violation example (synthetic):**
```c
void *buffer = malloc(64);
uint8_t *data = (uint8_t *)buffer;  /* MISRA 11.5 */
```

**Compliant rewrite:**
```c
/* Avoid malloc entirely in safety code */
static uint8_t buffer[64];
uint8_t *data = buffer;
```

**Memory aid:** void* casts bypass the type system — and malloc is also Rule 21.3.
**AUTOSAR context:** Generic callback parameters, NvM block addresses.

---

## Rule 12.1 — Operator precedence not relied upon (Advisory)

**Full rule text:** The precedence of operators within expressions should
be made explicit.

**Violation example (synthetic):**
```c
uint8_t result = a + b & mask;  /* Is this (a+b)&mask or a+(b&mask)? */
```

**Compliant rewrite:**
```c
uint8_t result = (a + b) & mask;  /* explicit — no ambiguity */
```

**Memory aid:** Add parentheses — they cost nothing and prevent review comments.
**AUTOSAR context:** Signal scaling formulas, bitmask operations.

---

## Rule 13.5 — No persistent side effects on right of && or || (Required)

**Full rule text:** The right hand operand of a logical && or || operator
shall not contain persistent side effects.

**Violation example (synthetic):**
```c
if ((get_mode() == MODE_RUN) && (++attempt_count < MAX_RETRIES)) {  /* MISRA 13.5 */
```

**Compliant rewrite:**
```c
attempt_count++;
if ((get_mode() == MODE_RUN) && (attempt_count < MAX_RETRIES)) {
```

**Memory aid:** Short-circuit evaluation may skip the right side — side effects become non-deterministic.
**AUTOSAR context:** State machine transition guards, error counter checks.

---

## Rule 14.4 — Controlling expression shall be essentially Boolean (Required)

**Full rule text:** The controlling expression of an if statement and
iteration statement shall be essentially Boolean.

**Violation example (synthetic):**
```c
uint8_t error_count = get_errors();
if (error_count) {  /* MISRA 14.4: not Boolean */
```

**Compliant rewrite:**
```c
uint8_t error_count = get_errors();
if (error_count != 0U) {
```

**Memory aid:** Explicit comparison states intent; implicit bool from integer is ambiguous.
**AUTOSAR context:** All conditional checks on status bytes, counter comparisons.

---

## Rule 15.5 — Single point of exit per function (Advisory)

**Full rule text:** A function should have a single point of exit at the end.

**Violation example (synthetic):**
```c
uint8_t validate_speed(uint16_t speed) {
    if (speed > MAX_SPEED) return ERROR_RANGE;   /* MISRA 15.5 */
    if (speed == 0U)       return ERROR_ZERO;    /* MISRA 15.5 */
    return STATUS_OK;
}
```

**Compliant rewrite:**
```c
uint8_t validate_speed(uint16_t speed) {
    uint8_t result;
    if (speed > MAX_SPEED)    { result = ERROR_RANGE; }
    else if (speed == 0U)     { result = ERROR_ZERO;  }
    else                      { result = STATUS_OK;   }
    return result;
}
```

**Memory aid:** One return = one place to set a breakpoint and reason about exit state.
**AUTOSAR context:** Input validation functions, state transition handlers.

---

## Rule 17.7 — Return value of non-void function shall be used (Required)

**Full rule text:** The value returned by a function having non-void return
type shall be used.

**Violation example (synthetic):**
```c
Rte_Write_VehicleSpeed(speed_value);  /* MISRA 17.7: return value discarded */
```

**Compliant rewrite:**
```c
Std_ReturnType ret = Rte_Write_VehicleSpeed(speed_value);
if (ret != E_OK) {
    Dem_ReportErrorStatus(DEM_EVENT_PORT_WRITE_ERROR, DEM_EVENT_STATUS_FAILED);
}
```

**Memory aid:** RTE and BSW APIs return error codes for a reason — check them.
**AUTOSAR context:** All RTE read/write calls, NvM, Dcm, Dem API calls.

---

## Rule 18.6 — Address of auto storage not copied beyond lifetime (Required)

**Full rule text:** The address of an object with automatic storage shall
not be copied to another object that persists after the first object
has ceased to exist.

**Violation example (synthetic):**
```c
static uint8_t *g_ptr;  /* global persists beyond function */

void init_buffer(void) {
    uint8_t local_buf[32];
    g_ptr = local_buf;  /* MISRA 18.6: local goes out of scope */
}
```

**Compliant rewrite:**
```c
static uint8_t g_buf[32];  /* make it static — persists */
static uint8_t *g_ptr = g_buf;
```

**Memory aid:** Stack memory is recycled — pointer to it after return is a time bomb.
**AUTOSAR context:** Callback registration, buffer passing to async BSW modules.

---

## Rule 18.8 — No variable length array types (Required)

**Full rule text:** Variable-length array types shall not be used.

**Violation example (synthetic):**
```c
void process_frames(uint8_t count) {
    uint8_t buffer[count];  /* MISRA 18.8: VLA — stack size unknown */
```

**Compliant rewrite:**
```c
#define MAX_FRAME_COUNT (64U)
void process_frames(uint8_t count) {
    uint8_t buffer[MAX_FRAME_COUNT];
    /* use count to limit loop, not array size */
```

**Memory aid:** VLAs make stack analysis impossible — critical for ASIL.
**AUTOSAR context:** Any buffer sized from runtime parameter.

---

## Rule 21.3 — Memory allocation functions not used (Required)

**Full rule text:** The memory allocation and deallocation functions of
<stdlib.h> shall not be used.

**Violation example (synthetic):**
```c
#include <stdlib.h>
uint8_t *buf = (uint8_t *)malloc(size);  /* MISRA 21.3 */
```

**Compliant rewrite:**
```c
/* Use static allocation with a fixed-size memory pool */
#define POOL_SIZE (256U)
static uint8_t pool[POOL_SIZE];
static uint16_t pool_index = 0U;

uint8_t *pool_alloc(uint16_t size) {
    uint8_t *ptr = NULL;
    if ((pool_index + size) <= POOL_SIZE) {
        ptr = &pool[pool_index];
        pool_index += size;
    }
    return ptr;
}
```

**Memory aid:** malloc can fail silently or fragment at runtime — both catastrophic in safety code.
**AUTOSAR context:** Any runtime memory request in ECU software — use static pools.
