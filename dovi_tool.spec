Summary:	CLI tool for working with Dolby Vision
Summary(pl.UTF-8):	Narzędzie CLI do pracy z Dolby Vision
Name:		dovi_tool
Version:	2.0.3
Release:	1
License:	MIT
Group:		Applications/Multimedia
#Source0Download: https://github.com/quietvoid/dovi_tool/releases/
Source0:	https://github.com/quietvoid/dovi_tool/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	e2350543569afecfad5082a966ffcdfd
# cd dovi_tool-%{version}
# cargo vendor
# cd ..
# tar cJf dovi_tool-vendor-%{version}.tar.xz dovi_tool-%{version}/{vendor,Cargo.lock}
Source1:	%{name}-vendor-%{version}.tar.xz
# Source1-md5:	cb38fbd418397f094a2547187266a35d
Patch0:		%{name}-x32.patch
URL:		https://github.com/quietvoid/dovi_tool
BuildRequires:	fontconfig-devel
BuildRequires:	cargo >= 1.64.0
BuildRequires:	cargo-c
BuildRequires:	rust >= 1.64.0
BuildRequires:	rpmbuild(macros) >= 2.004
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
ExclusiveArch:	%{x8664} %{ix86} x32 aarch64 armv6hl armv7hl armv7hnl
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
dovi_tool is a CLI tool combining multiple utilities for working with
Dolby Vision.

%description -l pl.UTF-8
dovi_tool to sterowany z linii poleceń program łączący wiele narzędzi
do pracy z Dolby Vision.

%package -n libdovi
Summary:	Library to read and write Dolby Vision metadata
Summary(pl.UTF-8):	Biblioteka do odczytu i zapisu metadanych Dolby Vision
Group:		Libraries

%description -n libdovi
Library to read and write Dolby Vision metadata.

%description -n libdovi -l pl.UTF-8
Biblioteka do odczytu i zapisu metadanych Dolby Vision.

%package -n libdovi-devel
Summary:	Header files for libdovi library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki libdovi
Group:		Development/Libraries
Requires:	libdovi = %{version}-%{release}

%description -n libdovi-devel
Header files for libdovi library.

%description -n libdovi-devel -l pl.UTF-8
Pliki nagłówkowe biblioteki libdovi.

%package -n libdovi-static
Summary:	Static libdovi library
Summary(pl.UTF-8):	Statyczna biblioteka libdovi
Group:		Development/Libraries
Requires:	libdovi-devel = %{version}-%{release}

%description -n libdovi-static
Static libdovi library.

%description -n libdovi-static -l pl.UTF-8
Statyczna biblioteka libdovi.

%prep
%setup -q -b1
%patch0 -p1

# use our offline registry
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source."git+https://github.com/plotters-rs/plotters"]
git = "https://github.com/plotters-rs/plotters"
replace-with = "vendored-sources"

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

# for tests only, not vendored from main dir
%{__sed} -i -e '/criterion/d' dolby_vision/Cargo.toml

%ifarch x32
# add pf-no-simd feature to pathfinder_simd dependency
echo 'features = ["pf-no-simd"]' >> vendor/pathfinder_geometry/Cargo.toml
%{__sed} -i -e 's/141871f41ab4ac7af854e54f1f637fb168ffbc97fdb57c60608f11b8eb95f1d7/6e731c54bfe9de2e7eb7963b748ac71cf5c9c371658525d906ba2c99ac136f79/' vendor/pathfinder_geometry/.cargo-checksum.json
%endif

%build
export CARGO_HOME="$(pwd)/.cargo"

%cargo_build --frozen

cd dolby_vision

cargo -v cbuild --offline --release --target %{rust_target} \
	--prefix %{_prefix} \
	--libdir %{_libdir}

%install
rm -rf $RPM_BUILD_ROOT

export CARGO_HOME="$(pwd)/.cargo"

%cargo_install --frozen \
	--path . \
	--root $RPM_BUILD_ROOT%{_prefix}

cd dolby_vision

cargo -v cinstall --frozen --release --target %{rust_target} \
	--destdir $RPM_BUILD_ROOT \
	--prefix %{_prefix} \
	--includedir %{_includedir} \
	--libdir %{_libdir}

%{__rm} $RPM_BUILD_ROOT%{_prefix}/.crates.toml
%{__rm} $RPM_BUILD_ROOT%{_prefix}/.crates2.json

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n libdovi -p /sbin/ldconfig
%postun	-n libdovi -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE README.md docs/{editor,generator,profiles}.md
%attr(755,root,root) %{_bindir}/dovi_tool

%files -n libdovi
%defattr(644,root,root,755)
%doc dolby_vision/{CHANGELOG.md,LICENSE,README.md}
%attr(755,root,root) %{_libdir}/libdovi.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libdovi.so.3

%files -n libdovi-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libdovi.so
%{_includedir}/libdovi
%{_pkgconfigdir}/dovi.pc

%files -n libdovi-static
%defattr(644,root,root,755)
%{_libdir}/libdovi.a
