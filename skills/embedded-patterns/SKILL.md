---
name: embedded-patterns
description: |
  Load automatically when any of these appear:
  embedded, bare metal, RTOS, FreeRTOS, QNX,
  Zephyr, interrupt, ISR, interrupt service
  routine, DMA, direct memory access, volatile,
  watchdog, WDT, stack overflow, heap, malloc,
  free, real-time, timing constraint, jitter,
  context switch, mutex, semaphore, ring buffer,
  circular buffer, state machine, FSM, bootloader,
  microcontroller, MCU, ECU software, peripheral,
  register, memory mapped IO, linker script,
  startup code, vector table, priority inversion,
  task scheduling, preemption, tick, timer,
  critical section, race condition, deadlock,
  memory barrier, cache coherency, MPU, memory
  protection unit, stack canary, stack depth,
  task stack, idle task, scheduler, cooperative,
  preemptive, tickless idle, low power mode.
---

## Safety-critical embedded rules

1. **No dynamic memory** in safety path (no malloc/free)
2. **No recursion** — stack depth must be statically provable
3. **Bounded loops only** — all loops have a defined maximum iteration count
4. **Watchdog always serviced** within the defined monitoring window
5. **Volatile for shared variables** between ISR and task/main context
6. **Atomic operations** for shared flags accessible from ISR
7. **Stack sizing** must include worst-case call depth + ISR nesting
8. **No blocking** in ISR — signal task, use flags, or write to ring buffer

---

## Common embedded C patterns

### State machine pattern
Preferred over if-else chains for ECU state management.
Each state is a function; transitions are explicit.

### Ring buffer pattern
Fixed-size circular buffer for ISR-to-task data.
Producer (ISR) writes; consumer (task) reads.
Head and tail pointers; full/empty detection.

### Non-blocking timer pattern
Software timer using a tick counter.
Compare current_tick to start_tick + period.
No busy-wait; no RTOS delay required.

### Memory pool pattern
Fixed-size block allocator replaces malloc.
Pool array statically allocated; allocation is
taking the next free block from a free-list.

### Interrupt-driven IO pattern
Peripheral generates interrupt on event.
ISR copies data to ring buffer; clears flag.
Task processes ring buffer in main context.

---

## RTOS design principles

- Assign task priorities from deadline: tighter deadline = higher priority
- Never hold a mutex across a task delay or blocking call
- ISR should never block — use semaphore/queue to signal tasks
- Stack size: measure at runtime with high-water mark, add 25% margin
- Priority inversion: use priority inheritance mutex when sharing with high-prio task

[reference: references/rtos-patterns.md]
[reference: references/interrupt-patterns.md]
