from agents import HandoffInputData


def payload_builder(output_type):
    def _on_handoff(ctx, filtered: output_type):
        """Required by SDK when input_type is set; no shared state needed."""
        return None

    def _input_filter(data: HandoffInputData) -> HandoffInputData:
        """Pass only classifier handoff payload to agent 3 (drop full history)."""
        handoff_call = next(
            (
                item
                for item in reversed(data.new_items)
                if getattr(item, "type", "") == "handoff_call_item"
            ),
            None,
        )

        if handoff_call is None:
            return data.clone(input_history=(), pre_handoff_items=(), new_items=())

        payload_json = handoff_call.raw_item.arguments
        return data.clone(
            input_history=({"role": "user", "content": payload_json},),
            pre_handoff_items=(),
            new_items=(),
        )

    return _on_handoff, _input_filter
