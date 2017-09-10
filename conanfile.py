from os import path
from conans import ConanFile, CMake, tools, util


class AzureiotsdkcConan(ConanFile):
    name = "Azure-IoT-SDK-C"
    version = "1.1.21"
    license = "https://github.com/Azure/azure-iot-sdk-c/blob/master/LICENSE"
    url = "https://github.com/bincrafters/conan-azure-iot-sdk-c"
    description = "A C99 SDK for connecting devices to Microsoft Azure IoT services"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = "Azure-C-Shared-Utility/1.0.41@bincrafters/stable", \
        "Azure-uMQTT-C/1.0.41@bincrafters/stable", \
        "Azure-uAMQP-C/1.0.41@bincrafters/stable", \
        "Parson/0.1.0@bincrafters/stable"
        
    release_name = "azure-iot-sdk-c-2017-08-11"

    def source(self):
        tools.get("https://github.com/Azure/azure-iot-sdk-c/archive/2017-08-11.tar.gz")

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.options.shared = False

        if self.settings.os == "Linux":
            self.options.shared = True

    def build(self):
        conan_magic_lines='''project(azure_iot_sdks)
        include(../conanbuildinfo.cmake)
        conan_basic_setup()
        '''
        self.copy(pattern="parson.h", dst=path.join(self.release_name, "parson"), src=self.deps_cpp_info["Parson"].include_paths[0])
        self.copy(pattern="parson.c", dst=path.join(self.release_name, "parson"), src=path.join(self.deps_cpp_info["Parson"].rootpath, "src"))
        tools.replace_in_file("%s/CMakeLists.txt" % self.release_name, "project(azure_iot_sdks)", conan_magic_lines)
        util.files.mkdir(path.join(self.deps_cpp_info["Azure-uAMQP-C"].include_paths[0], "azureiot"))
        util.files.mkdir(path.join(self.deps_cpp_info["Azure-uMQTT-C"].include_paths[0], "azureiot"))
        cmake = CMake(self)
        cmake.definitions["build_as_dynamic"] = self.options.shared
        cmake.definitions["skip_samples"] = True
        cmake.definitions["use_installed_dependencies"] = True
        cmake.definitions["azure_c_shared_utility_DIR"] = self.deps_cpp_info["Azure-C-Shared-Utility"].res_paths[0]
        cmake.definitions["uamqp_DIR"] = self.deps_cpp_info["Azure-uAMQP-C"].res_paths[0]
        cmake.definitions["umqtt_DIR"] = self.deps_cpp_info["Azure-uMQTT-C"].res_paths[0]
        cmake.definitions["AZURE_C_SHARED_UTILITY_INCLUDES"] = self.deps_cpp_info["Azure-C-Shared-Utility"].include_paths[0]
        cmake.configure(source_dir=self.release_name)
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst=".", src=".")
        self.copy(pattern="*", dst="include", src=path.join(self.release_name, "iothub_client", "inc"))
        self.copy(pattern="*", dst="include", src=path.join(self.release_name, "iothub_service_client", "inc"))
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()
