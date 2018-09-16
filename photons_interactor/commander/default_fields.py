from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb

finder_field = dictobj.Field(sb.overridden("{finder}"), formatted=True)
target_field = dictobj.Field(sb.overridden("{targets.lan}"), formatted=True)
db_queue_field = dictobj.Field(sb.overridden("{db_queue}"), formatted=True)
commander_field = dictobj.Field(sb.overridden("{commander}"), formatted=True)
progress_cb_field = dictobj.Field(sb.overridden("{progress_cb}"), formatted=True)
final_future_field = dictobj.Field(sb.overridden("{final_future}"), formatted=True)
request_future_field = dictobj.Field(sb.overridden("{request_future}"), formatted=True)
server_options_field = dictobj.Field(sb.overridden("{server_options}"), formatted=True)
request_handler_field = dictobj.Field(sb.overridden("{request_handler}"), formatted=True)
protocol_register_field = dictobj.Field(sb.overridden("{protocol_register}"), formatted=True)

refresh_field = dictobj.NullableField(sb.boolean
    , help = """
        Whether to refresh our idea of what is on the network"

        If this is False then we will use the cached notion of what's on the network.
      """
    )

timeout_field = dictobj.Field(sb.float_spec, default=20
    , help = "The max amount of time we wait for replies from the lights"
    )

matcher_field = dictobj.NullableField(sb.or_spec(sb.string_spec(), sb.dictionary_spec())
    , help = """
        What lights to target. If this isn't specified then we interact with all
        the lights that can be found on the network.

        This can be specfied as either a space separated key=value string or as
        a dictionary.

        For example,
        "label=kitchen,bathroom location_name=home"
        or
        ``{"label": ["kitchen", "bathroom"], "location_name": "home"}``

        See https://delfick.github.io/photons-core/modules/photons_device_finder.html#valid-filters
        for more information on what filters are available.
      """
    )

pkt_type_field = dictobj.Field(sb.or_spec(sb.integer_spec(), sb.string_spec()), wrapper=sb.required
    , help = """
        The type of packet to send to the lights. This can be a number or
        the name of the packet as known by the photons framework.

        A list of what's available can be found at
        https://delfick.github.io/photons-core/binary_protocol.html
      """
    )

pkt_args_field = dictobj.NullableField(sb.dictionary_spec()
    , help = """
        A dictionary of fields that make up the payload of the packet we
        are sending to the lights.
      """
    )
