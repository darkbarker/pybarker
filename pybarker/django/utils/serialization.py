from itertools import chain

from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model, ManyToManyField, ForeignKey, FileField, ImageField
from django.db.models.fields.files import FieldFile, ImageFieldFile
from django.db.models.query import QuerySet


# само поле тип: django.db.models.fields.files.FileField
# питоновское значение этого поля должно быть: django.db.models.fields.files.FieldFile
def jsonify_fieldfile(fieldfile):
    if not fieldfile:  # защита от The attribute "blabla" has no file associated with it. которое возникает походу если пустая строка вместо NULL в бд
        return None
    try:
        return {
            "size": fieldfile.size,
            "file": "%s" % fieldfile.url,
        }
    except Exception as e:
        return {
            "size": 0,
            "file": "%s" % fieldfile.url,
            "error": str(e),
        }


# само поле тип: django.db.models.fields.files.ImageField
# питоновское значение этого поля должно быть: django.db.models.fields.files.ImageFieldFile
def jsonify_ImageFieldFile(imagefieldfile):
    if not imagefieldfile:  # см. выше
        return None
    try:
        return {
            "size": imagefieldfile.size,
            "file": "%s" % imagefieldfile.url,
            "width": imagefieldfile.width,
            "height": imagefieldfile.height,
        }
    except Exception as e:
        return {
            "size": 0,
            "file": "%s" % imagefieldfile.url,
            "error": str(e),
            "width": 0,
            "height": 0,
        }


# сделано на основе штатного model_to_dict
def jsonify_model(instance, fieldsonly=None):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        # if not getattr(f, 'editable', False):
        #    continue
        is_foreign = isinstance(f, ForeignKey)
        if fieldsonly:
            if is_foreign:
                if f.column not in fieldsonly:
                    continue
            else:
                if f.name not in fieldsonly:
                    continue
            # TODO тут проверить ManyToManyField аналогично как работает
        # if exclude and f.name in exclude:
        #    continue
        if is_foreign:
            # f.name - segment, f.column - segment_id
            data[f.column] = f.value_from_object(instance)
        elif isinstance(f, ManyToManyField):
            # name, column - directions
            # print(f, type(f), f.__dict__)
            # ol = f.value_from_object(instance)
            # for o in ol:
            #     print(o, type(o))
            data["%s_ids" % f.column] = [mod.id for mod in f.value_from_object(instance)]
        elif isinstance(f, GenericForeignKey):
            pass  # там всегда editable=False в GenericForeignKey, в оригинале не используется потому, но оно нам и не нужно
        # elif isinstance(f, FileField):
        #    data[f.name] = jsonify_fieldfile(f.value_from_object(instance))  # FileField.FieldFile, рисуем структуру ручками
        else:
            data[f.name] = f.value_from_object(instance)
    return data


# енкодер для джосона более полноценный, умеющий сериализовать по возможности всё
class ApiDjangoJSONEncoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, QuerySet):
            return list(o)
        elif isinstance(o, set):
            return list(o)
        elif isinstance(o, Model):
            return jsonify_model(o, self.fieldsonly)
        elif isinstance(o, ImageFieldFile):
            return jsonify_ImageFieldFile(o)
        elif isinstance(o, FieldFile):
            return jsonify_fieldfile(o)
        else:
            try:
                return super().default(o)
            except TypeError as e:
                # чёрный ход, попытка взять __str__ если уж он совсем не дефолтный, почему бы нет
                if hasattr(o, "__str__") and o.__str__ is not object.__str__:
                    return str(o)
                raise e
