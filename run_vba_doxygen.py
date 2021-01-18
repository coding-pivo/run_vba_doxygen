import os
import argparse
import time
import sys

try:
    # Try Python 2
    import ConfigParser as configparser
except ImportError:
    # Try Python 3 if Python 2 was not working
    import configparser

def get_time():
    """
    Function to return the current time. This is needed to make the script
    compatible with different versions of Python as time.clock() is deprecated
    since version 3.3 and was removed in version 3.8
    :return: Current time
    """
    try:
        # Try to use new function introduced with Python 3.3
        return time.perf_counter()
    except AttributeError:
        # Use older time.clock() if time.pref_counter() does not exist
        return time.clock()

def main():
    start = get_time()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate Doxygen documentation for VB project')
    parser.add_argument('config_file', type=str, help='config file name')
    args = parser.parse_args()

    print('Reading parameter from config file: {}'.format(os.path.abspath(args.config_file)))

    # Parse config file
    config = configparser.ConfigParser()
    config.read(args.config_file)

    # Check if mandatory section is available in config file
    if not config.has_section('General'):
        sys.exit('Error: Section \'General\' is missing in config file')

    # Get doxyfile name
    if config.has_option('General', 'DOXYFILE'):
        doxyfile = config.get('General', 'DOXYFILE')
        # Throw an error if parameter is empty
        if not doxyfile:
            sys.exit('Error: Parameter \'DOXYFILE\' is empty')
    else:
        sys.exit('Error: Parameter \'DOXYFILE\' is missing in config file')

    # Get source/input directory
    input_path = None
    if config.has_option('General', 'INPUT_PATH'):
        input_path = config.get('General', 'INPUT_PATH')

    # Get output directory
    output_path = None
    if config.has_option('General', 'OUTPUT_PATH'):
        output_path = config.get('General', 'OUTPUT_PATH')

    # Get DOT directory
    dot_path = None
    if config.has_option('General', 'DOT_PATH'):
        dot_path = config.get('General', 'DOT_PATH')

    # Get awk executable
    if config.has_option('General', 'AWK_PROG'):
        awk_prog = config.get('General', 'AWK_PROG')
        # Throw an error if parameter is empty
        if not awk_prog:
            sys.exit('Error: Parameter \'AWK_PROG\' is empty')
    else:
        sys.exit('Error: Parameter \'AWK_PROG\' is missing in config file')

    # Get awk script location
    if config.has_option('General', 'AWK_FILTER_SCRIPT'):
        awk_filter_script = config.get('General', 'AWK_FILTER_SCRIPT')
        # Throw an error if parameter is empty
        if not awk_filter_script:
            sys.exit('Error: Parameter \'AWK_FILTER_SCRIPT\' is empty')
    else:
        sys.exit('Error: Parameter \'AWK_FILTER_SCRIPT\' is missing in config file')

    # Get Doxygen executable
    if config.has_option('General', 'DOXYGEN_PROG'):
        doxygen_prog = config.get('General', 'DOXYGEN_PROG')
        # Throw an error if parameter is empty
        if not doxygen_prog:
            sys.exit('Error: Parameter \'DOXYGEN_PROG\' is empty')
    else:
        sys.exit('Error: Parameter \'DOXYGEN_PROG\' is missing in config file')

    # Create filter batch file to be used in Doxyfile (INPUT_FILTER)
    filter_file_name = 'filter.bat'
    with open(filter_file_name, 'w') as f: # open file in write mode and create if not existing
        f.write('"{}" -f "{}" %*%\n'.format(awk_prog, awk_filter_script))
    filter_file_name = os.path.abspath('filter.bat')

    print('Generate documentation...')

    # Generate shell command dependent on given parameters
    # If one parameter is empty (input, output or dot) don't change it on the command line
    # and use the one defined in the Doxyfile

    # Set first part of shell command
    command = '( type {} & echo INPUT_FILTER={} '.format(doxyfile, filter_file_name)

    # Add input path to shell commend if not empty (otherwise Doxyfile content is used)
    if input_path:
        command += '& echo INPUT={} '.format(input_path)

    # Add output path to shell commend if not empty (otherwise Doxyfile content is used)
    if output_path:
        command += '& echo OUTPUT_DIRECTORY={} '.format(output_path)

    # Add DOT path to shell commend if not empty (otherwise Doxyfile content is used)
    if dot_path:
        command += '& echo DOT_PATH={} '.format(dot_path)

    # Set final part of shell command
    command += ') | {} -'.format(doxygen_prog)

    # Run shell command (call Doxygen)
    os.system(command)

    end = get_time()

    print('Done...')
    print('It took {} to generate documentation'.format(time.strftime('%H:%M:%S', time.gmtime(end - start))))

    sys.exit(0)

if __name__ == '__main__':
    main()
