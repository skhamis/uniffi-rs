{%- let rec = ci|get_record_definition(name) %}
class {{ type_name }}:
    {% for field in rec.fields() %}
        {{- field.name()|var_name }}: "{{- field|type_name }}";
    {%- endfor %}

    {%- if rec.has_fields() %}
    @typing.no_type_check
    def __init__(self, {% for field in rec.fields() %}
    {{- field.name()|var_name }}: "{{- field|type_name }}"
    {%- if field.default_value().is_some() %} = _DEFAULT{% endif %}
    {%- if !loop.last %}, {% endif %}
    {%- endfor %}):
        {%- for field in rec.fields() %}
        {%- let field_name = field.name()|var_name %}
        {%- match field.default_value() %}
        {%- when None %}
        self.{{ field_name }} = {{ field_name }}
        {%- when Some with(literal) %}
        if {{ field_name }} is _DEFAULT:
            self.{{ field_name }} = {{ literal|literal_py(field) }}
        else:
            self.{{ field_name }} = {{ field_name }}
        {%- endmatch %}
        {%- endfor %}
    {%- endif %}

    def __str__(self):
        return "{{ type_name }}({% for field in rec.fields() %}{{ field.name()|var_name }}={}{% if loop.last %}{% else %}, {% endif %}{% endfor %})".format({% for field in rec.fields() %}self.{{ field.name()|var_name }}{% if loop.last %}{% else %}, {% endif %}{% endfor %})

    def __eq__(self, other):
        {%- for field in rec.fields() %}
        if self.{{ field.name()|var_name }} != other.{{ field.name()|var_name }}:
            return False
        {%- endfor %}
        return True

class {{ ffi_converter_name }}(_UniffiConverterRustBuffer):
    @staticmethod
    def read(buf):
        return {{ type_name }}(
            {%- for field in rec.fields() %}
            {{ field.name()|var_name }}={{ field|read_fn }}(buf),
            {%- endfor %}
        )

    @staticmethod
    def write(value, buf):
        {%- if rec.has_fields() %}
        {%- for field in rec.fields() %}
        {{ field|write_fn }}(value.{{ field.name()|var_name }}, buf)
        {%- endfor %}
        {%- else %}
        pass
        {%- endif %}
