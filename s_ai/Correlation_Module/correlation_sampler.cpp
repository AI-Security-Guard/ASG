#include <torch/extension.h>
#include <vector>
#include <iostream>

// CPU 버전 함수 선언
torch::Tensor correlation_cpp_forward(
    torch::Tensor input1,
    torch::Tensor input2,
    int kH, int kW,
    int patchH, int patchW,
    int padH, int padW,
    int dilationH, int dilationW,
    int dilation_patchH, int dilation_patchW,
    int dH, int dW);

std::vector<torch::Tensor> correlation_cpp_backward(
    torch::Tensor input1,
    torch::Tensor input2,
    torch::Tensor grad_output,
    int kH, int kW,
    int patchH, int patchW,
    int padH, int padW,
    int dilationH, int dilationW,
    int dilation_patchH, int dilation_patchW,
    int dH, int dW);

// CPU-only 인터페이스
torch::Tensor correlation_sample_forward(
    torch::Tensor input1,
    torch::Tensor input2,
    int kH, int kW,
    int patchH, int patchW,
    int padH, int padW,
    int dilationH, int dilationW,
    int dilation_patchH, int dilation_patchW,
    int dH, int dW) {
    return correlation_cpp_forward(input1, input2, kH, kW, patchH, patchW,
                                   padH, padW, dilationH, dilationW,
                                   dilation_patchH, dilation_patchW, dH, dW);
}

std::vector<torch::Tensor> correlation_sample_backward(
    torch::Tensor input1,
    torch::Tensor input2,
    torch::Tensor grad_output,
    int kH, int kW,
    int patchH, int patchW,
    int padH, int padW,
    int dilationH, int dilationW,
    int dilation_patchH, int dilation_patchW,
    int dH, int dW) {
    return correlation_cpp_backward(input1, input2, grad_output, kH, kW, patchH, patchW,
                                    padH, padW, dilationH, dilationW,
                                    dilation_patchH, dilation_patchW, dH, dW);
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("forward", &correlation_sample_forward, "Spatial Correlation Sampler Forward");
    m.def("backward", &correlation_sample_backward, "Spatial Correlation Sampler Backward");
}
