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
        self.parent_datastore = parent_datastore
        self.current_value = None
        self.default_value = None

        self.record_name = ""
        self.is_array = False
        self.is_array_2d = False
        self.use_max_value = False
        self.use_min_value = False

        self.activex_name = ""
        self.alternative_activex_name = ""

    @property
    def value(self):
        """Get value of record."""
        return self.current_value

    def __str__(self):
        """Get string representation of record."""
        return str(self.current_value)

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
                datastore_record.array_length_2d = json["array_length_2d"]
                datastore_record.array_length_ref_2d_name = json["array_length_ref_2d"]

        else:
            datastore_record = cls(parent_datastore)

        datastore_record.current_value = json["current_value"]
        datastore_record.default_value = json["default_value"]
        datastore_record.record_name = json["record_name"]
        datastore_record.activex_name = json["activex_name"]
        datastore_record.alternative_activex_name = json["alternative_activex_name"]
        datastore_record.is_array = json["is_array"]
        datastore_record.is_array_2d = json["is_array_2d"]
        datastore_record.use_max_value = json["use_max_value"]
        datastore_record.use_min_value = json["use_min_value"]

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
        return self.parent_datastore.get_variable_record(self.array_length_ref_name)


class DataStoreRecordArray2D(DataStoreRecord):
    """2D Array object to store data records from Motor-CAD."""

    def __init__(self, parent_datastore):
        """Do initialisation."""
        super().__init__(parent_datastore)
        self.array_length_2d = [-1, -1]
        self.array_length_ref_2d_name = []
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
                self.parent_datastore.get_variable_record(array_length_ref_name)
            ]
        return array_length_2d_array


class Datastore(dict):
    """Datastore object."""

    def __init__(self):
        """Do initialisation."""
        super().__init__()
        self.__activex_names__ = {} # Lookup table to allow alternative activex names.

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

    @classmethod
    def from_json(cls, datastore_json):
        """Create a Datastore object from JSON data."""
        datastore = cls()

        for datastore_record_json in datastore_json["data_records"]:
            datastore_record_object = DataStoreRecord.from_json(datastore_record_json, datastore)
            datastore[datastore_record_json["activex_name"]] = datastore_record_object

            datastore.__activex_names__[
                datastore_record_json["activex_name"].lower()
                ] = datastore_record_json["activex_name"]
            if datastore_record_json["alternative_activex_name"] != "xxx":
                # Parameter also has an alternative name. Add it to another dict to search quickly.
                datastore.__activex_names__[
                    datastore_record_json["alternative_activex_name"].lower()
                    ] = datastore_record_json["activex_name"]


        return datastore
