param(
    [string]$Checkout = "$env:USERPROFILE\git\llama.cpp-omni"
)

$ErrorActionPreference = "Stop"
$cmake = "C:\Program Files\CMake\bin\cmake.exe"
$vulkanSdk = Get-ChildItem "C:\VulkanSDK" -Directory |
    Sort-Object Name -Descending |
    Select-Object -First 1

if (-not (Test-Path -LiteralPath "$Checkout\CMakeLists.txt")) {
    throw "Clone https://github.com/tc-mb/llama.cpp-omni.git to $Checkout first."
}
if (-not (Test-Path -LiteralPath $cmake)) {
    throw "CMake is missing. Install Kitware.CMake with Winget."
}
if ($null -eq $vulkanSdk) {
    throw "Vulkan SDK is missing. Install KhronosGroup.VulkanSDK with Winget."
}

$env:VULKAN_SDK = $vulkanSdk.FullName
$env:Path = "$env:VULKAN_SDK\Bin;$env:Path"
$buildDir = Join-Path $Checkout "build-vulkan"

& $cmake -S $Checkout -B $buildDir -DGGML_VULKAN=ON -DGGML_NATIVE=OFF -DCMAKE_BUILD_TYPE=Release
& $cmake --build $buildDir --config Release --target voxcpm2-cli --parallel 8
