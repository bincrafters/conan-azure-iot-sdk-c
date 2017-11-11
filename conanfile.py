import os
from conans import ConanFile, CMake, tools


class AzureiotsdkcConan(ConanFile):
    name = "Azure-IoT-SDK-C"
    version = "1.1.27"
    release_date = "2017-10-20"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/bincrafters/conan-azure-iot-sdk-c"
    description = "A C99 SDK for connecting devices to Microsoft Azure IoT services"
    license = "https://github.com/Azure/azure-iot-sdk-c/blob/master/LICENSE"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    lib_short_name = "azure_iot_sdks"
    root_dir = "%s-%s" % (name.lower(), release_date)
    requires = "Azure-C-Shared-Utility/[>=1.0.46]@bincrafters/stable", \
        "Azure-uMQTT-C/[>=1.0.46]@bincrafters/stable", \
        "Azure-uAMQP-C/[>=1.0.46]@bincrafters/stable", \
        "Azure-uHTTP-C/[>=1.0.46]@bincrafters/stable", \
        "Parson/0.1.0@bincrafters/stable"

    def source(self):
        source_url = "https://github.com/Azure/azure-iot-sdk-c"
        tools.get("%s/archive/%s.tar.gz" % (source_url, self.release_date))

    def configure(self):
        # XXX (uilian): Some linkage errors must be solved on Windows
        if self.settings.os == "Windows":
            self.options.shared = False
        # XXX (uilian): hidden symbol `curl_easy_getinfo' when libcurl is static
        if self.settings.os != "Windows":
            self.options["libcurl"].shared = True

    def build(self):
        cmake_file = os.path.join(self.root_dir, "CMakeLists.txt")
        conan_magic_lines = """project(azure_iot_sdks)
        include(../conanbuildinfo.cmake)
        CONAN_BASIC_SETUP()
        """
        tools.replace_in_file(cmake_file, "project(azure_iot_sdks)", conan_magic_lines)
        tools.replace_in_file(cmake_file, 'include("dependencies.cmake")', "")
        tools.replace_in_file(cmake_file, 'set_platform_files(${CMAKE_CURRENT_LIST_DIR}/c-utility)', "")
        if self.settings.os == "Windows":
            cmake_file = os.path.join(self.root_dir, "iothub_client", "CMakeLists.txt")
            conan_magic_lines = "target_link_libraries(iothub_client_dll ${iothub_client_libs} ${CONAN_LIBS} Winhttp)"
            tools.replace_in_file(cmake_file, 'target_link_libraries(iothub_client_dll ${iothub_client_libs})', conan_magic_lines)

        parson_dst = os.path.join(self.root_dir, "deps", "parson")
        self.copy(pattern="parson.h", dst=parson_dst, src=self.deps_cpp_info["Parson"].include_paths[0])
        self.copy(pattern="parson.c", dst=parson_dst, src=os.path.join(self.deps_cpp_info["Parson"].rootpath, "src"))
        with tools.chdir(self.root_dir):
            cmake = CMake(self)
            cmake.definitions["build_as_dynamic"] = self.settings.os == "Windows" and self.options.shared
            cmake.definitions["skip_samples"] = True
            cmake.definitions["use_installed_dependencies"] = True
            if self.settings.os == "Windows" and self.options.shared:
                cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
            cmake.configure(source_dir=os.getcwd())
            cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst=".", src=".")
        self.copy(pattern="*", dst="include", src=os.path.join(self.root_dir, "iothub_client", "inc"))
        self.copy(pattern="*", dst="include", src=os.path.join(self.root_dir, "iothub_service_client", "inc"))
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.libs.append("Winhttp")
