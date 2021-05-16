from .base_options import BaseOptions

class ServerOptions(BaseOptions):
    def initialize(self):
        BaseOptions.initialize(self)
        self.parser.add_argument('--results_dir', type=str, default='./results/', help='saves results here.')
        self.parser.add_argument('--aspect_ratio', type=float, default=1.0, help='aspect ratio of result images')
        self.parser.add_argument('--phase', type=str, default='test', help='train, val, test, etc')
        self.parser.add_argument('--which_epoch', type=str, default='latest', help='which epoch to load? set to latest to use latest cached model')     
        self.parser.add_argument('--cluster_path', type=str, default='features_clustered_010.npy', help='the path for clustered results of encoded features')
        self.parser.add_argument('--use_encoded_image', action='store_true', help='if specified, encode the real image to get the feature map')
        self.parser.add_argument("--export_onnx", type=str, help="export ONNX model to a given file")
        self.parser.add_argument("--engine", type=str, help="run serialized TRT engine")
        self.parser.add_argument("--onnx", type=str, help="run ONNX model via TRT")
        self.parser.add_argument('--ip', type=str, help='server ip')
        self.parser.add_argument('--port', type=int, help='server port')

        # Network Structure
        self.parser.add_argument("--arch", type=str, default='resnet101')
        # Data Preference
        self.parser.add_argument("--data-dir", type=str, default='./data/LIP')
        self.parser.add_argument("--batch-size", type=int, default=1)
        self.parser.add_argument("--input-size", type=str, default='473,473')
        self.parser.add_argument("--num-classes", type=int, default=20)
        self.parser.add_argument("--ignore-label", type=int, default=255)
        self.parser.add_argument("--random-mirror", action="store_true")
        self.parser.add_argument("--random-scale", action="store_true")
        
        # Evaluation Preference
        self.parser.add_argument("--log-dir", type=str, default='./log')
        self.parser.add_argument("--model-restore", type=str, default='./human_parse/checkpoints/exp-schp-201908261155-lip.pth')
        self.parser.add_argument("--gpu", type=str, default='0', help="choose gpu device.")
        self.parser.add_argument("--save-results", action="store_true", help="whether to save the results.")
        self.parser.add_argument("--flip", action="store_true", help="random flip during the test.")
        self.parser.add_argument("--multi-scales", type=str, default='1', help="multiple scales during the test")

        self.isTrain = False
