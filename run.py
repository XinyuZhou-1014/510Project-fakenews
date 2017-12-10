from fakenews_model import FakeNewsModel

DEFAULT_INPUT_FILE = "test_input.txt"
DEFAULT_OUTPUT_FILE = "test_output.txt"
DEFAULT_MODEL_FILE = 'gbdt_res_with_w2v.pickle'


if __name__ == "__main__":
    print("Server start.")
    print("Put file at test_input.txt (will be delete)") 
    server = FakeNewsModel()   
    server.input_output(DEFAULT_INPUT_FILE, 
                        DEFAULT_OUTPUT_FILE, 
                        DEFAULT_MODEL_FILE)