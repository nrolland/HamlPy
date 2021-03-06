import re

class Element(object):
    """contains the pieces of an element and can populate itself from haml element text"""
    
    self_closing_tags = ('meta', 'img', 'link', 'script', 'br', 'hr')
    haml_regex = r"(?P<tag>%\w+)?(?P<id>#\w*)?(?P<class>\.[\w\.]*)*(?P<attributes>\{.*\})?(?P<selfclose>/)?(?P<django>=)?(?P<inline>[^\w\.#\{].*)?"

    ELEMENT = '%'
    ID = '#'
    CLASS = '.'
    
    def __init__(self, haml):
        self.haml = haml
        self.tag = None
        self.id = None
        self.classes = None
        self.attributes = ''
        self.self_close = False
        self.django_variable = False
        self.inline_content = ''
        self._parse_haml()
        
    def _parse_haml(self):
        split_tags = re.search(self.haml_regex, self.haml).groupdict('')
        
        self.attributes_dict = self._parse_attribute_dictionary(split_tags.get('attributes'))
        self.tag = split_tags.get('tag').strip(self.ELEMENT) or 'div'
        self.id = self._parse_id(split_tags.get('id'))
        self.classes = ('%s %s' % (split_tags.get('class').lstrip(self.CLASS).replace('.', ' '), " ".join(self.attributes_dict.get('class', '')))).strip()
        self.self_close = split_tags.get('selfclose') or self.tag in self.self_closing_tags
        self.django_variable = split_tags.get('django') != '' #or split_tags.get('djangoattr') != ''
        self.inline_content = split_tags.get('inline').strip()
    #print split_tags

    def joinarray(self, char, obj):
        if isinstance(obj, str):
            text = char + obj
        else:
            text = ''
            for one_id in obj:
                text += char + one_id
        return text

    def _parse_id(self, id_haml):
        id_text = id_haml.strip(self.ID)
        if 'id' in self.attributes_dict:
            id_text += self.joinarray('', self._expand_django(self.attributes_dict['id']))
        id_text = id_text.lstrip('')
        return id_text
    
    def _expand_django(self, obj):
        #print obj
        if isinstance(obj, str):
            split_tags = re.search(self.haml_regex, obj).groupdict('')
            #print "tags", split_tags
            if split_tags.get('django') != '':
                obj = "{{"  + split_tags.get('inline').strip() + "}}"
                #print "found", obj
            return obj
        else:
            ret = []
            for one_id in obj:
                ret.append(self._expand_django(one_id))
            return tuple(ret)

                
    def _parse_attribute_dictionary(self, attribute_dict_string):        
        attributes_dict = {}
        if (attribute_dict_string):
            attributes_dict = eval(attribute_dict_string)
            for k, v in attributes_dict.items():
                if k != 'id' and k != 'class':
                    v= self._expand_django(v)
                    separator = "" if k == 'href' else " "
                    self.attributes += "%s='%s' " % (k, self.joinarray(separator, v).lstrip(" "))
            self.attributes = self.attributes.strip()
        return attributes_dict
        
