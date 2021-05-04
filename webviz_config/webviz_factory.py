class WebvizFactory:
    """Base class for all factories that want to register themselves in
    WebvizFactoryRegistry.
    """

    def cleanup_resources_after_plugin_init(self):
        """Will be called after all plugins have been initialized to allow the factory
        to do clean-up of any temporary resources allocated during the initialization
        phase. The base implementation does nothing, override this function to
        perform factory-specific cleanup.
        """
