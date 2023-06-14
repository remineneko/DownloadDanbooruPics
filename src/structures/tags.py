import itertools
import warnings

from dataclasses import dataclass
from typing import Any, Union, Dict, List

from media_metadata import MediaMetadata


@dataclass
class TagContent:
    content: List[MediaMetadata]


class Tags:
    """
    This class represents a list of tags that has been loaded.
    It stores the attributes of a tag, namely, name and metadata related to images found.

    All fields must have the same ``__len__`` which is the number of tags.

    This structure is similar to Instances in Detectron 2; however, this is modified to fit with how this program works.
    """

    def __init__(self, **kwargs):
        self._fields: Dict[str, Any] = {}
        for k, v in kwargs.items():
            self.set(k, v)

    def __setattr__(self, name: str, val: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, val)
        else:
            self.set(name, val)

    def __getattr__(self, name: str) -> Any:
        if name == "_fields" or name not in self._fields:
            raise AttributeError("Cannot find field '{}' in the given Tags!".format(name))
        return self._fields[name]

    def set(self, name: str, value: Any) -> None:
        """
        Set the field named `name` to `value`.
        The length of `value` must be the number of instances,
        and must agree with other existing fields in this object.
        """
        with warnings.catch_warnings(record=True):
            data_len = len(value)
        if len(self._fields):
            assert (
                len(self) == data_len
            ), "Adding a field of length {} to a Tags of length {}".format(data_len, len(self))
        self._fields[name] = value

    def has(self, name: str) -> bool:
        """
        Returns:
            bool: whether the field called `name` exists.
        """
        return name in self._fields

    def remove(self, name: str) -> None:
        """
        Remove the field called `name`.
        """
        del self._fields[name]

    def get(self, name: str) -> Any:
        """
        Returns the field called `name`.
        """
        return self._fields[name]

    def get_fields(self) -> Dict[str, Any]:
        """
        Returns:
            dict: a dict which maps names (str) to data of the fields

        Modifying the returned dict will modify this instance.
        """
        return self._fields

    def __getitem__(self, item: Union[int, str]) -> "Tags":
        """
        Args:
            item: an index-like object and will be used to index all the fields.

        Returns:
            If `item` is a string, return the data in the corresponding field.
            Otherwise, returns a `Tags` where all fields are indexed by `item`.
        """
        if type(item) == int:
            if item >= len(self) or item < -len(self):
                raise IndexError("Instances index out of range!")
            else:
                item = slice(item, None, len(self))

        ret = Tags()
        for k, v in self._fields.items():
            ret.set(k, v[item])
        return ret

    def __len__(self) -> int:
        for v in self._fields.values():
            # use __len__ because len() has to be int and is not friendly to tracing
            return v.__len__()
        raise NotImplementedError("Empty Tags does not support __len__!")

    def __iter__(self):
        raise NotImplementedError("`Tags` object is not iterable!")
    
    @staticmethod
    def cat(tag_lists: List["Tags"]) -> "Tags":
        """
        Args:
            tag_lists (list[Tags])

        Returns:
            Tags
        """
        assert all(isinstance(i, Tags) for i in tag_lists)
        assert len(tag_lists) > 0
        if len(tag_lists) == 1:
            return tag_lists[0]

        ret = Tags()
        for k in tag_lists[0]._fields.keys():
            values = [i.get(k) for i in tag_lists]
            v0 = values[0]
            if isinstance(v0, list):
                values = list(itertools.chain(*values))
            elif hasattr(type(v0), "cat"):
                values = type(v0).cat(values)
            else:
                raise ValueError("Unsupported type {} for concatenation".format(type(v0)))
            ret.set(k, values)
        return ret

    def __str__(self) -> str:
        s = self.__class__.__name__ + "("
        s += "num_tags={}, ".format(len(self))
        s += "fields=[{}])".format(", ".join((f"{k}: {v}" for k, v in self._fields.items())))
        return s
    