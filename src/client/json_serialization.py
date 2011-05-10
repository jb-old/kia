#!../../bin/python2.7
from __future__ import division, print_function, unicode_literals

import base64
import json

class JSONSerializer(object):
    """Provides JSON serialization for a set of classes."""
    
    default_type_property = "__type"
    
    default_indent = None
    default_separators = (",", ":")
    
    def __init__(self, types=None, type_property=None,
                 indent=None, separators=None, **root_options):
        if types:
            self.types = dict(types)
        else:
            self.types = None
        
        self.root_options = options
        
        if type_property is None:
            self.type_property = self.default_type_property
        
        if separators is None:
            self.separators = self.default_separators
        
        if indent is None:
            indent = self.default_indent
        
        if sort_keys is not None:
            self.sort_keys = sort_keys
        
        self.raw_encoder = json.JSONEncoder(
            allow_nan=False,
            sort_keys=True,
            indent=indent,
            separators=separators,
            default=self.produce_json_equivalent
        )
        
        self.dump = self.raw_encoder.dump
        self.dumps = self.raw_encoder.dumps
        
        self.raw_decoder = json.JSONDecoder(
            object_hook=self.parse_json_equivalent,
            parse_constant=self._parse_constant
        )
        
        self.load = self.raw_decoder.load
        self.loads = self.raw_decoder.loads
    
    _constants = {
        "true": True,
        "false": False,
        "null": None
    }
    
    def _parse_constant(self, name):
        return self._constants[name]
    
    def parse_json_equivalent(self, o):
        if self.type_property in o and o[self.type_property] in self.types:
            return (self.types[o[self.type_property]]
                    .from_json_equivalent(o, *self.options))
        else:
            return o
    
    def produce_json_equivalent(self, o, options=None):
        for type_name, cls in self.types.items():
            if isinstance(o, cls):
                json_type = type_name
        else:
            raise TypeError("Type not known to serializer: {}"
                            .format(type(o).__name__))
        
        if options is None:
            options = self.root_options
        
        if hasattr(o, "to_dynamic_json_equivalent"):
            def recur(o, **changes):
                return self.produce_json_equivalent(o, dict(options, **changes))
            
            return o.to_dynamic_json_equivalent(recur, **options)
        elif hasattr(o, "to_json_equivalent"):
            return o.to_json_equivalent()
        else:
            raise TypeError("{}s can not be JSON-serialized."
                            .format(type(o).__name__))
