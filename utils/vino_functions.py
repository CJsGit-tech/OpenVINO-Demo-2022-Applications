from openvino.inference_engine import IECore
import cv2
import numpy as np

def PrepareNetWork(model_xml,model_bin,device,flag=None):


    if flag == 'onnx':
        ie = IECore()
        net = ie.read_network(model = model_xml)

    else:
        ie = IECore()
        net = ie.read_network(model = model_xml,weights = model_bin)

    # ####################### Very Important #############################################
    # # Check to make sure that the plugin has support for all layers in the model
    # supported_layers = ie.query_network(net,device_name = device)
    # unsupported_layers = [layer for layer in supported_layers.values() if layer!= device]
    # if len(unsupported_layers)>0:
    #     raise Exception(f"Number of unsupported layers {len(unsupported_layers)}")
    # ####################################################################################
    

    exec_net = ie.load_network(network=net, device_name = device)

    # Store name of input and output blobs
    input_blob = next(iter(net.input_info))
    output_blob = next(iter(net.outputs))

    # Extract Dimension (n:batch, c:color channel,h: height, w: width )
    n, c ,h ,w = net.input_info[input_blob].input_data.shape
    print('Extract Model Input Dimension:',n,c,h,w)
    
    return (input_blob,output_blob), exec_net, (n,c,h,w)

def PrepareInputImage(image,image_shape):
    n,c,h,w = image_shape

    if c == 1:
        in_frame = cv2.resize(image,(w,h))
        in_frame = in_frame.reshape((w,h,c))
        in_frame = in_frame.transpose((2,0,1)) # Moving color channels to head
        in_frame = in_frame.reshape((n,c,h,w))
        return image,in_frame

    else:
        # Resize
        in_frame = cv2.resize(image,(w,h))
        in_frame = in_frame.transpose((2,0,1)) # Moving color channels to head
        in_frame = in_frame.reshape((n,c,h,w))
        return image, in_frame

def MakePrediction(execution_network, input_blob, inference_frame):
    # Run Inference
    result = execution_network.infer(inputs = {input_blob:inference_frame})
    
    return result