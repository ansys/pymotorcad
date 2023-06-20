"""Methods for adaptive geometry."""


class _RpcMethodsAdaptiveGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def add_adaptive_parameter(self, name):
        """

        Parameters
        ----------
        name

        Returns
        -------

        """

        method = "AddAdaptiveParameter"
        params = [name]
        return self.connection.send_and_receive(method)

    def set_adaptive_parameter_value(self, name):
        """

        Parameters
        ----------
        name

        Returns
        -------

        """
        method = "SetAdaptiveParameterValue"
        params = [name]
        return self.connection.send_and_receive(method)

    def get_adaptive_parameter_value(self, name):
        """

        Parameters
        ----------
        name

        Returns
        -------

        """
        pass

    def get_region(self, name, region):
        """

        Parameters
        ----------
        name
        region

        Returns
        -------

        """
        pass

    def set_region(self, region):
        """

        Parameters
        ----------
        region

        Returns
        -------

        """
        pass

    def get_entities_between_poly_start_end(self, region, polyline):
        """

        Parameters
        ----------
        region
        polyline

        Returns
        -------

        """
        pass

    def check_closed_region(self, region):
        """

        Parameters
        ----------
        region

        Returns
        -------

        """
        pass

    def check_collisions(self, region):
        """

        Parameters
        ----------
        region

        Returns
        -------

        """
        pass

    def add_adaptive_region(self, region):
        """

        Parameters
        ----------
        region

        Returns
        -------

        """
        pass

    def save_adaptive_script(self, filepath):
        """

        Parameters
        ----------
        filepath

        Returns
        -------

        """
        pass
