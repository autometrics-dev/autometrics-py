from opentelemetry import trace


def get_exemplar():
    """Generates an exemplar dictionary from the current implicit OTel context if available"""
    span_context = trace.get_current_span().get_span_context()

    # Only include the exemplar if it is valid and sampled
    if span_context.is_valid and span_context.trace_flags.sampled:
        # You must set the trace_id and span_id exemplar labels like this to link OTel and
        # Prometheus. They must be formatted as hexadecimal strings.
        return {
            "trace_id": trace.format_trace_id(span_context.trace_id),
            "span_id": trace.format_span_id(span_context.span_id),
        }

    return None
