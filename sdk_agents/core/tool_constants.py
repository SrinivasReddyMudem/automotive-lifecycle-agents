"""
Tool selection constants for automotive ECU debug agents.

LAYER_TOOL_MAP: 2D mapping {protocol: {osi_layer: [ranked_tools]}}
Used by validators to verify tool_selection.primary is appropriate for the
detected protocol and OSI layer. First tool in each list is the preferred choice.
"""

# Canonical tool names — use these exact strings in tool_selection fields
OSCILLOSCOPE = "Oscilloscope"
DMM = "DMM"
CANOE = "CANoe"
CANANALYZER = "CANalyzer"
PCAN = "PCAN"
TRACE32 = "TRACE32"
DLT_VIEWER = "DLT Viewer"
WIRESHARK = "Wireshark"
INCA = "INCA"
LIN_ANALYSER = "LIN Analyser"
NETWORK_ANALYSER = "Network Analyser"
VEHICLE_SPY = "VehicleSpy"

# 2D lookup: {protocol: {layer: [tools_in_preference_order]}}
LAYER_TOOL_MAP: dict[str, dict[str, list[str]]] = {
    "CAN": {
        "L1 Physical": [OSCILLOSCOPE, DMM, "CAN Termination Meter"],
        "L2 Data Link": [CANOE, PCAN, CANANALYZER],
        "L3-L4 Network": [CANOE, TRACE32],
        "L7 Application": [CANOE, DLT_VIEWER, TRACE32],
        "MCU Execution": [TRACE32, DLT_VIEWER],
        "RTOS": [TRACE32, DLT_VIEWER],
    },
    "CAN-FD": {
        "L1 Physical": [OSCILLOSCOPE, DMM],
        "L2 Data Link": [CANOE, PCAN, CANANALYZER],
        "L7 Application": [CANOE, DLT_VIEWER, TRACE32],
        "MCU Execution": [TRACE32, DLT_VIEWER],
    },
    "LIN": {
        "L1 Physical": [OSCILLOSCOPE, LIN_ANALYSER],
        "L2 Data Link": [CANOE, LIN_ANALYSER, "LDF Viewer"],
        "L7 Application": [CANOE, DLT_VIEWER],
    },
    "Ethernet": {
        "L1 Physical": [OSCILLOSCOPE, NETWORK_ANALYSER, "TDR"],
        "L2 Data Link": [WIRESHARK, "CANoe Ethernet"],
        "L3-L4 Network": [WIRESHARK, "Tcpdump"],
        "L7 Application": [WIRESHARK, DLT_VIEWER, "DoIP Tester"],
        "MCU Execution": [TRACE32, DLT_VIEWER],
    },
    "RTOS": {
        "Physical": [OSCILLOSCOPE, "Logic Analyser"],
        "RTOS": [TRACE32, DLT_VIEWER],
        "Application": ["TRACE32 Watch", DLT_VIEWER],
        "MCU Execution": [TRACE32, DLT_VIEWER],
    },
    "UDS": {
        "L7 Application": ["CANoe Diagnostics", INCA, VEHICLE_SPY],
        "L3-L4 Network": [CANOE, WIRESHARK],
        "L2 Data Link": [CANOE, PCAN],
    },
    "FlexRay": {
        "L1 Physical": [OSCILLOSCOPE, "FlexRay Analyser"],
        "L2 Data Link": [CANOE, "CANalyzer FlexRay"],
    },
    "Unknown": {
        "L1 Physical": [OSCILLOSCOPE, DMM],
        "L2 Data Link": [CANOE, PCAN],
        "L7 Application": [DLT_VIEWER, TRACE32],
        "MCU Execution": [TRACE32, DLT_VIEWER],
    },
}

# All valid protocol names — used by ProtocolDetection schema Literal validation
KNOWN_PROTOCOLS = list(LAYER_TOOL_MAP.keys())

# Flat set of all valid tool names — used by _check_tool_selection
ALL_KNOWN_TOOLS: set[str] = {
    tool
    for layer_map in LAYER_TOOL_MAP.values()
    for tools in layer_map.values()
    for tool in tools
}


def get_tools_for(protocol: str, osi_layer: str) -> list[str]:
    """
    Return the list of appropriate tools for a protocol + OSI layer combination.
    Returns empty list if the combination is not in the map (validator treats as unknown).
    Performs case-insensitive partial match on osi_layer.
    """
    proto_map = LAYER_TOOL_MAP.get(protocol, {})
    # Exact match first
    if osi_layer in proto_map:
        return proto_map[osi_layer]
    # Partial match — "L1 Physical / something" should still match "L1 Physical"
    osi_lower = osi_layer.lower()
    for key, tools in proto_map.items():
        if key.lower() in osi_lower or osi_lower in key.lower():
            return tools
    return []
