from input_algorithms import spec_base as sb

def signature(spec):
    if isinstance(spec, sb.integer_spec):
        yield "integer"
    if isinstance(spec, sb.float_spec):
        yield "float"
    elif isinstance(spec, sb.string_spec):
        yield "string"
    elif isinstance(spec, sb.boolean):
        yield "boolean"
    elif isinstance(spec, sb.dictionary_spec):
        yield "dictionary"
    elif isinstance(spec, sb.string_choice_spec):
        choices = " | ".join(spec.choices)
        yield f"choice of ({choices})"

    elif isinstance(spec, sb.optional_spec):
        yield from signature(spec.spec)
        yield "(optional)"
    elif isinstance(spec, sb.defaulted):
        yield from signature(spec.spec)
        dflt = spec.default(None)
        if isinstance(dflt, str):
            dflt = f'"{dflt}"'
        yield f"(default {dflt})"
    elif isinstance(spec, sb.required):
        yield from signature(spec.spec)
        yield "(required)"
    elif isinstance(spec, sb.listof):
        yield '['
        yield from signature(spec.spec)
        yield ', ... ]'
    elif isinstance(spec, sb.dictof):
        yield '{'
        yield from signature(spec.name_spec)
        yield ':'
        yield from signature(spec.value_spec)
    elif isinstance(spec, (sb.container_spec, sb.formatted)):
        yield from signature(spec.spec)
