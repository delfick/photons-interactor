from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb

finder_field = dictobj.Field(sb.overridden("{finder}"), formatted=True)
target_field = dictobj.Field(sb.overridden("{targets.lan}"), formatted=True)
refresh_field = dictobj.NullableField(sb.boolean)
timeout_field = dictobj.Field(sb.integer_spec, default=20)
matcher_field = dictobj.NullableField(sb.or_spec(sb.string_spec(), sb.dictionary_spec()))
protocol_register_field = dictobj.Field(sb.overridden("{protocol_register}"), formatted=True)
