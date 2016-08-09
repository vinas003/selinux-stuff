Name          : SMHI-SELinux
Summary       : Package that installs %{name}
Version       : 20160809
Release       : 1
License       : SMHI
Group         : Applications/System
URL           : www.smhi.se
BuildRoot     : %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Source0       : SMHI.te
Requires      : policycoreutils-python setools-console

# Packages needed to build the rpm
BuildRequires : selinux-policy-devel

# Define the path to our files
%define SMHISELinuxPath /etc/smhi/SELinux

%description
Package that installs %{name}
This package installs SMHIs SELinux policy
For more info contact tfolinux@smhi.se

%prep

%build 

%install

# Make sure the buildroot is clean
rm -rf %{buildroot}

# Create the directory structure
mkdir -p %{buildroot}/%{SMHISELinuxPath}

# Cd into and copy the source file
cd %{buildroot}/%{SMHISELinuxPath}
cp %{SOURCE0} ./

# Create the symlink to selinux Makefile
ln -s /usr/share/selinux/devel/Makefile

# Compile the policy
make

# Remove not needed files create by the compiler
rm -rf SMHI.fc SMHI.if SMHI.tpm tmp 

%pre

# Ensure that SELinux is running and is Enforcing
SELinuxStatus=$(getenforce)
if [ $SELinuxStatus != "Enforcing" ]
then
    echo -e "\nEnsure SELinux is running and is enforcing\n"
    exit 1
fi

%post

# Load the policy
semodule -i %{SMHISELinuxPath}/SMHI.pp

# If we are doing an install (NOT upgrading) the package
if [ $1 == 1 ] 
then
    # Change the filecontext on /local_disk before we install the SMHI SELinux module
    semanage fcontext -a -t SMHI_storage_t "/local_disk(/.*)?"
    restorecon -R -v /local_disk/
fi

%preun

# If we are uninstalling (NOT upgrading) the package
if [ $1 == 0 ]
then
    # Change the filecontext back on /local_disk before we uninstall the SMHI SELinux module
    semanage fcontext -d -t SMHI_storage_t "/local_disk(/.*)?"
    restorecon -R -v /local_disk/
    
    # Unload the SELinux policy
    semodule -r SMHI    
fi

%clean

rm -rf %{buildroot}

%files

%defattr(-,root,root,-)

%dir %attr(0755, root, root) %{SMHISELinuxPath}
%attr(0644, root, root) %{SMHISELinuxPath}/SMHI.te
%attr(0644, root, root) %{SMHISELinuxPath}/SMHI.pp
%{SMHISELinuxPath}/Makefile

%changelog
* Tue Aug 09 2016 Victor Näslund <victor.naslund@smhi.se> 20160809-1
- Initial version
