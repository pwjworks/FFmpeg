from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.apple import fix_apple_shared_install_name


class ffmpegRecipe(ConanFile):
    name = "ffmpeg"
    version = "7.0"
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "*"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        self.cpp.package.bindirs = ["bin"]
        self.cpp.package.libdirs = ["lib"]
        self.cpp.package.includedirs = ["include"]

    def generate(self):
        at_toolchain = AutotoolsToolchain(self)
        tools_path = "/home/pwjworks/android-ndk-r26d-linux/android-ndk-r26d/toolchains/llvm/prebuilt/linux-x86_64/bin"
        cc = tools_path + "/aarch64-linux-android%s-clang" % str(
            self.settings.os.api_level
        )
        cxx = tools_path + "/aarch64-linux-android%s-clang++" % str(
            self.settings.os.api_level
        )
        nm = tools_path + "/llvm-nm"
        llvm_ar = tools_path + "/llvm-ar"
        at_toolchain.configure_args.extend(
            [
                "--enable-small",
                "--enable-gpl",
                "--enable-pic",
                "--enable-neon",
                "--enable-jni",
                "--enable-cross-compile",
                "--enable-hardcoded-tables",
                "--disable-programs",
                "--disable-avdevice",
                "--disable-doc",
                "--disable-symver",
                "--disable-postproc",
                "--disable-x86asm",
                "--disable-stripping",
                "--cc=%s" % cc,
                "--cxx=%s" % cxx,
                "--nm=%s" % nm,
                "--ar=%s" % llvm_ar,
                "--target-os=android",
            ]
        )
        at_toolchain.configure_args.remove("--sbindir=${prefix}/bin")
        at_toolchain.configure_args.remove("--includedir=${prefix}/include")
        at_toolchain.configure_args.remove("--oldincludedir=${prefix}/include")
        at_toolchain.configure_args.remove("--host=aarch64-linux-android")
        at_toolchain.configure_args.remove("--build=x86_64-linux-gnu")
        if self.settings.arch == "x86":
            at_toolchain.configure_args.append("--cpu=x86")
            at_toolchain.configure_args.append("--arch=x86")
        elif self.settings.arch == "x86_64":
            at_toolchain.configure_args.append("--cpu=x86_64")
            at_toolchain.configure_args.append("--arch=x86_64")
        elif self.settings.arch == "armv8":
            at_toolchain.configure_args.append("--cpu=armv8-a")
            at_toolchain.configure_args.append("--arch=aarch64")
        elif self.settings.arch == "armv7":
            at_toolchain.configure_args.append("--cpu=armv7-a")
            at_toolchain.configure_args.append("--arch=arm")

        if self.settings.build_type == "Debug":
            at_toolchain.configure_args.append("--enable-debug=3")
            at_toolchain.configure_args.append("--disable-stripping")
        elif self.settings.build_type == "Release":
            at_toolchain.configure_args.append("--disable-debug")
        at_toolchain.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = [
            "avcodec",
            "avfilter",
            "avformat",
            "avutil",
            "swresample",
            "swscale",
        ]
