from pose_estimator.networks import GeneralPoseModel


class Handler():
    def __init__(self, model_path):
        self.model_path = model_path
        self.network = GeneralPoseModel(model_path)
    
    def predict(self, img_path):
        _, conf = self.network.predict(img_path)
        
        return conf
