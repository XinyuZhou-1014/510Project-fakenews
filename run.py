from predict_engine import FakeNewsModel

DEFAULT_INPUT_FILE = "./temp/test_input.txt"
DEFAULT_OUTPUT_FILE = "./temp/test_output.txt"
DEFAULT_MODEL_FILE = './fakenews_models/lgbm_res.txt'
DEFAULT_TOP_WORDS = 10000


if __name__ == "__main__":
    if DEFAULT_TOP_WORDS != 10000:
        print("Sorry, the prediction model now only support top 10000 words")
        DEFAULT_TOP_WORDS = 10000

    print("Server start.")
    print("Put file at test_input.txt (will be delete)")
    server = FakeNewsModel(model_file=DEFAULT_MODEL_FILE, top=DEFAULT_TOP_WORDS)
    server.input_output(DEFAULT_INPUT_FILE,
                        DEFAULT_OUTPUT_FILE,
                        DEFAULT_MODEL_FILE)
