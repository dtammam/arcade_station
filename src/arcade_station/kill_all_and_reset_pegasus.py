from arcade_station.core.core_functions import kill_processes

def main():
    """
    Main function to kill all specified processes and reset Pegasus.
    """
    print("Killing all specified processes...")
    kill_processes()
    print("All specified processes have been killed.")
    # Add any additional logic to reset Pegasus if needed

if __name__ == "__main__":
    main() 


from arcade_station import core, listeners

def test_core_functions():
    config = core.core_functions.load_config('default_config.toml')
    print("Config loaded:", config)
    core.core_functions.open_header('TestScript')

def test_listeners():
    listeners.main()

if __name__ == "__main__":
    test_core_functions()
    test_listeners()