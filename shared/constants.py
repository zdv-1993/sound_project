# Commands__________________________________________________
COMMAND_UPLOAD_WITH_PARAMS = "upload_file_with_params"
COMMAND_GET_FILE_PARAMS = "get_file_params"
COMMAND_GET_FILE_DATA = "get_file_data"
COMMAND_GET_FILES_LIST = "get_files_list"
# End commands_______________________________________________

# File constants
FILE_SERVER_HOST = "file_app"
FILE_SERVER_PORT = 50000
# End file constants_________________________________________

# Responses
READY_TO_UPLOAD = "ready_to_upload"
SUCCESS = "success"
READY_TO_UPLOAD_RESPONSE = {"message": READY_TO_UPLOAD}
SUCCESS_RESPONSE = {"message": SUCCESS}


ALREADY_EXIST_ERROR = "file already exists"
ALREADY_EXIST_RESPONSE = {"error": ALREADY_EXIST_ERROR}

HASH_DOES_NOT_COMPARE = "hash does not compare"
HASH_DOES_NOT_COMPARE_RESPONSE = {"error": HASH_DOES_NOT_COMPARE}

UPLOADING_ERROR = "file not uploaded. Write error"
UPLOADING_ERROR_RESPONSE = {"error": UPLOADING_ERROR}

FILE_NOT_FOUND_ERROR = "file not found"
FILE_NOT_FOUND_RESPONSE = {"error": FILE_NOT_FOUND_ERROR}


SENDED_BYTES_COUNT = 1024