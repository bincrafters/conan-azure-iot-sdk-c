import os
from conans import ConanFile, CMake, tools, util


class AzureiotsdkcConan(ConanFile):
    name = "Azure-IoT-SDK-C"
    version = "1.1.27"
    release_date = "2017-11-03"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/bincrafters/conan-azure-iot-sdk-c"
    description = "A C99 SDK for connecting devices to Microsoft Azure IoT services"
    license = "https://github.com/Azure/azure-iot-sdk-c/blob/master/LICENSE"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    lib_short_name = "azure_iot_sdks"
    requires = "Azure-C-Shared-Utility/[>=1.0.46]@bincrafters/stable", \
        "Azure-uMQTT-C/[>=1.0.46]@bincrafters/stable", \
        "Azure-uAMQP-C/[>=1.0.46]@bincrafters/stable", \
        "Parson/0.1.0@bincrafters/stable"
        
    def source(self):
        source_url = "https://github.com/Azure/azure-iot-sdk-c"
        tools.get("%s/archive/%s.tar.gz" % (source_url, self.release_date))
        extracted_dir = "%s-%s" % (self.name.lower(), self.release_date)
        os.rename(extracted_dir,"sources")

    def build(self):
        parson_dst = os.path.join("sources", "parson")
        self.copy(pattern="parson.h", dst=parson_dst, src=self.deps_cpp_info["Parson"].include_paths[0])
        self.copy(pattern="parson.c", dst=parson_dst, src=os.path.join(self.deps_cpp_info["Parson"].rootpath, "src"))
        util.files.mkdir(os.path.join(self.deps_cpp_info["Azure-uAMQP-C"].include_paths[0], "azureiot"))
        util.files.mkdir(os.path.join(self.deps_cpp_info["Azure-uMQTT-C"].include_paths[0], "azureiot"))
        cmake = CMake(self)
        cmake.definitions["build_as_dynamic"] = self.options.shared
        cmake.definitions["skip_samples"] = True
        cmake.definitions["use_installed_dependencies"] = True
        cmake.definitions["azure_c_shared_utility_DIR"] = self.deps_cpp_info["Azure-C-Shared-Utility"].res_paths[0]
        cmake.definitions["uamqp_DIR"] = self.deps_cpp_info["Azure-uAMQP-C"].res_paths[0]
        cmake.definitions["umqtt_DIR"] = self.deps_cpp_info["Azure-uMQTT-C"].res_paths[0]
        cmake.definitions["AZURE_C_SHARED_UTILITY_INCLUDES"] = self.deps_cpp_info["Azure-C-Shared-Utility"].include_paths[0]
        cmake.configure(source_dir="sources")
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst=".", src=".")
        self.copy(pattern="*", dst="include", src=os.path.join("sources", "iothub_client", "inc"))
        self.copy(pattern="*", dst="include", src=os.path.join("sources", "iothub_service_client", "inc"))
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()
