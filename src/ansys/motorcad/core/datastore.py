# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Contains data classes for getting whole datastore from Motor-CAD."""


class DataStoreRecord:
    """Object to store data records from Motor-CAD.

    Parameters
    ----------
    parent_datastore : Datastore
        records must belong to a dataStore
    """

    def __init__(self, parent_datastore):
        """Do initialisation."""
        self._parent_datastore = parent_datastore
        self.current_value = None
        self.default_value = None

        self.units = None
        self.input_or_output_type = None

        self.record_name = ""
        self.activex_name = ""
        self.alternative_activex_name = ""
        self.file_section = ""

        self.is_array = False
        self.is_array_2d = False
        self.use_max_value = False
        self.use_min_value = False
        self.max_value = None
        self.min_value = None

    @property
    def value(self):
        """Get value of record."""
        return self.current_value

    def __str__(self):
        """Get string representation of record."""
        return str(self.current_value)

    def update_parent(self, parent_datastore):
        """Update the reference to the parent datastore this DataStoreRecord is contained in.

        Parameters
        ----------
        parent_datastore : Datastore
        """
        self._parent_datastore = parent_datastore

    def file_section_in_list(self, section_list):
        """Check if this record is part of the list of file sections.

        Parameters
        ----------
        section_list : list | None
            list of strings that define the category (e.g. Magnetics, Dimensions, Winding, etc).

        Returns
        -------
        bool
        """
        if section_list is None:
            return True
        else:
            return self.file_section in section_list

    def inout_in_list(self, inout_list):
        """Check if this record is part of the list of input_or_output_type.

        Parameters
        ----------
        inout_list : list | None
            list of integers that define the data type (e.g. input type, compatibility type, etc).

        Returns
        -------
        bool
        """
        if inout_list is None:
            return True
        else:
            return self.input_or_output_type in inout_list

    def to_json(self):
        """Convert DatastoreRecord to a serialisable dictionary for JSON export.

        Returns
        -------
        dict
        """
        record_dict = {
            "current_value": self.current_value,
            "default_value": self.default_value,
            "units": self.units,
            "input_or_output_type": self.input_or_output_type,
            "record_name": self.record_name,
            "activex_name": self.activex_name,
            "alternative_activex_name": self.alternative_activex_name,
            "file_section": self.file_section,
            "is_array": self.is_array,
            "is_array_2d": self.is_array_2d,
            "use_max_value": self.use_max_value,
            "use_min_value": self.use_min_value,
            "max_value": self.max_value,
            "min_value": self.min_value,
        }
        return record_dict

    @classmethod
    def from_json(cls, json, parent_datastore):
        """Create a DataStore object from JSON data.

        Parameters
        ----------
        json : dict
            JSON data returned from Motor-CAD
        parent_datastore : Datastore
            records must belong to a dataStore

        Returns
        -------
        DataStoreRecord or DataStoreRecordArray or DataStoreRecordArray2D
        """
        if json["is_array"]:
            datastore_record = DataStoreRecordArray(parent_datastore)
            datastore_record.dynamic = json["dynamic"]
            if datastore_record.dynamic:
                datastore_record.array_length = json["array_length"]
                datastore_record.array_length_ref_name = json["array_length_ref"]

        elif json["is_array_2d"]:
            datastore_record = DataStoreRecordArray2D(parent_datastore)
            datastore_record.dynamic = json["dynamic"]
            if datastore_record.dynamic:
                datastore_record.array_length_2d = tuple(json["array_length_2d"])
                datastore_record.array_length_ref_2d_name = tuple(json["array_length_ref_2d"])

        else:
            datastore_record = cls(parent_datastore)

        datastore_record.current_value = json["current_value"]
        datastore_record.default_value = json["default_value"]

        datastore_record.units = json["units"]
        datastore_record.input_or_output_type = json["input_or_output_type"]

        datastore_record.record_name = json["record_name"]
        datastore_record.activex_name = json["activex_name"]
        datastore_record.alternative_activex_name = json["alternative_activex_name"]
        datastore_record.file_section = json["file_section"]

        datastore_record.is_array = json["is_array"]
        datastore_record.is_array_2d = json["is_array_2d"]
        datastore_record.use_max_value = json["use_max_value"]
        datastore_record.use_min_value = json["use_min_value"]
        if datastore_record.use_max_value:
            datastore_record.max_value = json["max_value"]
        if datastore_record.use_min_value:
            datastore_record.min_value = json["min_value"]

        return datastore_record


class DataStoreRecordArray(DataStoreRecord):
    """Array object to store data records from Motor-CAD.

    Parameters
    ---------
    parent_datastore : DataStore
        records must belong to a dataStore
    """

    def __init__(self, parent_datastore):
        """Do initialisation."""
        super().__init__(parent_datastore)
        self.array_length = -1
        self.array_length_ref_name = ""
        self.dynamic = False

    @property
    def array_length_ref(self):
        """Get array length record for current record.

        Returns
        -------
        int
        """
        return self._parent_datastore.get_variable_record(self.array_length_ref_name)

    def to_json(self):
        """Convert 1D array Datastore record to a serialisable dictionary for JSON export.

        Returns
        -------
        dict
        """
        record_dict = super().to_json()
        record_dict["array_length"] = self.array_length
        record_dict["array_length_ref"] = self.array_length_ref_name
        record_dict["dynamic"] = self.dynamic
        return record_dict


class DataStoreRecordArray2D(DataStoreRecord):
    """2D Array object to store data records from Motor-CAD."""

    def __init__(self, parent_datastore):
        """Do initialisation."""
        super().__init__(parent_datastore)
        self.array_length_2d = (-1, -1)
        self.array_length_ref_2d_name = ("", "")
        self.dynamic = False

    @property
    def array_length_ref_2d(self):
        """Get array of array length records for current record.

        Returns
        -------
        int
        """
        array_length_2d_array = []
        for array_length_ref_name in self.array_length_ref_2d_name:
            array_length_2d_array += [
                self._parent_datastore.get_variable_record(array_length_ref_name)
            ]
        return array_length_2d_array

    def to_json(self):
        """Convert 2D array Datastore record to a serialisable dictionary for JSON export.

        Returns
        -------
        dict
        """
        record_dict = super().to_json()
        record_dict["array_length_2d"] = self.array_length_2d
        record_dict["array_length_ref_2d"] = self.array_length_ref_2d_name
        record_dict["dynamic"] = self.dynamic
        return record_dict


class Datastore(dict):
    """Datastore object."""

    def __init__(self):
        """Do initialisation."""
        super().__init__()
        self.__activex_names__ = {}  # Lookup table to allow alternative activex names.

    def get_variable_record(self, variable_name):
        """Get a variable record case-insensitive.

        Parameters
        ----------
        variable_name : str

        Returns
        -------
        DataStoreRecord
        """
        try:
            return self[self.__activex_names__[variable_name.lower()]]
        except KeyError:
            # Variable doesn't exist in the datastore. Return nothing.
            return None

    def get_variable(self, variable_name):
        """Get a variable value case insensitive.

        Parameters
        ----------
        variable_name : str

        Returns
        -------
        DataStoreRecord
        """
        if self.get_variable_record(variable_name) is not None:
            return self.get_variable_record(variable_name).value
        return None

    def filter_variables(self, file_sections=None, inout_types=None):
        """Filter the datastore by file section and input-or-output type.

        Parameters
        ----------
        file_sections : list | None
            variable section (category in automation parameter names)
        inout_types : list | None
            Input/Output type (e.g. input, compatibility, setting).

        Returns
        -------
        DataStore
        """
        result = dict(
            (key, item)
            for key, item in self.items()
            if item.file_section_in_list(file_sections) and item.inout_in_list(inout_types)
        )

        return Datastore.from_dict(result)

    def to_json(self):
        """Return serialised version of the Datastore object to be saved as a JSON.

        Returns
        -------
        dict
        """
        record_list = [value.to_json() for key, value in self.items()]
        return {"data_records": record_list}

    def to_dict(self):
        """Cast Datastore class to a dictionary with the current_value.

        Returns
        -------
        dict
        """
        return dict((key, item.current_value) for key, item in self.items())

    def pop(self, k, d=None):
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.

        If the key is not found, return the default if given; otherwise,
        raise a KeyError.
        """

        if self.get_variable_record(k) is not None:
            # key exists in the dictionary. Need to remove from activex_names.
            record = self.get_variable_record(k)
            if record.alternative_activex_name != "xxx":
                # Remove alternative name as well.
                self.__activex_names__.pop(record.alternative_activex_name.lower())

            # Ensure the actual activex name is being removed, not the alternative.
            self.__activex_names__.pop(record.activex_name.lower())
            return super().pop(record.activex_name, d)
        else:
            # Keep behaviour of returning a KeyError if not in the dict.
            if d is not None:
                return d
            else:
                raise KeyError

    def extend(self, datastore: "Datastore"):
        """Extend the current datastore using data from the provided Datastore.

        Returns
        -------
        Datastore
        """
        for key, value in datastore.items():
            self[key] = value
            self[key].update_parent(self)

            self.__activex_names__[key.lower()] = key
            if value.alternative_activex_name != "xxx":
                # Parameter also has an alternative name. Add it to another dict to search quickly.
                self.__activex_names__[value.alternative_activex_name.lower()] = key
        return self

    @classmethod
    def from_json(cls, datastore_json):
        """Create a Datastore object from JSON data."""
        datastore = cls()

        for datastore_record_json in datastore_json["data_records"]:
            datastore_record_object = DataStoreRecord.from_json(datastore_record_json, datastore)
            datastore[datastore_record_json["activex_name"]] = datastore_record_object

            datastore.__activex_names__[datastore_record_json["activex_name"].lower()] = (
                datastore_record_json["activex_name"]
            )
            if datastore_record_json["alternative_activex_name"] != "xxx":
                # Parameter also has an alternative name. Add it to another dict to search quickly.
                datastore.__activex_names__[
                    datastore_record_json["alternative_activex_name"].lower()
                ] = datastore_record_json["activex_name"]

        return datastore

    @classmethod
    def from_dict(cls, datastore_dict):
        """Create a Datastore object from a dictionary of DataStoreRecords."""
        datastore = cls()

        for key, value in datastore_dict.items():
            datastore[key] = value
            datastore[key].update_parent(datastore)

            datastore.__activex_names__[key.lower()] = key
            if value.alternative_activex_name != "xxx":
                # Parameter also has an alternative name. Add it to another dict to search quickly.
                datastore.__activex_names__[value.alternative_activex_name.lower()] = key

        return datastore
