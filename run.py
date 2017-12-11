from fakenews_model import FakeNewsModel

DEFAULT_INPUT_FILE = "test_input.txt"
DEFAULT_OUTPUT_FILE = "test_output.txt"
DEFAULT_MODEL_FILE = 'gbdt_res_with_w2v.pickle'
DEFAULT_TOP_WORDS = 10000


if __name__ == "__main__":
    if DEFAULT_TOP_WORDS != 10000:
        print("Sorry, the prediction model now only support top 10000 words")
        DEFAULT_TOP_WORDS = 10000

    print("Server start.")
    print("Put file at test_input.txt (will be delete)")
    server = FakeNewsModel(top=DEFAULT_TOP_WORDS)
    server.input_output(DEFAULT_INPUT_FILE,
                        DEFAULT_OUTPUT_FILE,
                        DEFAULT_MODEL_FILE)
