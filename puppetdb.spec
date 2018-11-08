# Application bin dir.
%global _app_bindir /usr/share/puppetdb/bin
# Bin dir the end user adds to their PATH
%global _ux_bindir /usr/bin
# Log directory
%global _app_logdir /var/log/puppet/puppetdb
# Run directory, PID files go here
%global _app_rundir /var/run/puppet/puppetdb

# Puppet Installation Layout
%global _sysconfdir /etc
%global _app_prefix /usr/share/puppetdb
%global _app_data /var/lib/puppetdb
%global _projconfdir %{_sysconfdir}/puppet/puppetdb
%global _symbindir /dev/null

%global rubylibdir        /usr/share/ruby/vendor_ruby

# Use the alternate locations for things.
%global _prefix          /usr/share/puppetdb
%global _rundir          /var/run

Name:             puppetdb
Version:          5.2.6
Release:          1%{?dist}

Summary:          Puppet Labs - puppetdb
Vendor:           Puppet Labs <info@puppetlabs.com>

License:          ASL 2.0

URL:              http://puppetlabs.com
Source0:          http://downloads.puppetlabs.com/%{name}/%{name}-%{version}.tar.gz
Source1:          http://downloads.puppetlabs.com/%{name}/%{name}-%{version}.tar.gz.asc
Patch0:           nosymlink.patch

Group:            System Environment/Base
BuildArch:        noarch

BuildRequires:    ruby
BuildRequires:    /usr/sbin/useradd

# Required to get trustanchors for java
BuildRequires:    ca-certificates

Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

Requires:         java-1.8.0-openjdk-headless
Requires:         bash

# net-tools is required for netstat usage in service unit file
# See: https://tickets.puppetlabs.com/browse/SERVER-338
Requires:         net-tools
Requires:         /usr/bin/which

# procps is required for pgrep, used in several of the init scripts
Requires:         procps

Requires:         puppet >= 4.99.0

%description
Puppet-integrated catalog and fact storage

%package termini
Summary: Termini for puppetdb
Requires: puppet-%{version}
Obsoletes: puppetdb-termini < %{version}
Provides:  puppetdb-termini >= %{version}

%description termini
Termini for puppetdb

%prep
%setup 
%patch0 -p1

%build

%install

rm -rf $RPM_BUILD_ROOT

env EZ_VERBOSE=1 DESTDIR=%{buildroot} prefix=%{_prefix} app_prefix=%{_app_prefix} app_data=%{_app_data} projconfdir=%{_projconfdir} bindir=%{_app_bindir} uxbindir=%{_ux_bindir} symbindir=%{_symbindir} rundir=%{_app_rundir} app_logdir=%{_app_logdir} defaultsdir=%{_sysconfdir}/sysconfig unitdir=%{_unitdir} bash install.sh systemd_redhat

env EZ_VERBOSE=1 DESTDIR=%{buildroot} rubylibdir=%{rubylibdir} prefix=%{_prefix} bash install.sh termini

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Note: changes to this section of the spec may require synchronisation with the
# install.sh source based installation methodology.
#
# Add puppetdb group
getent group puppetdb > /dev/null || \
  groupadd -r puppetdb || :
# Add puppetdb user
if getent passwd puppetdb > /dev/null; then
  usermod --gid puppetdb --home %{_app_data} \
  --comment "puppetdb daemon" puppetdb || :
else
  useradd -r --gid puppetdb --home %{_app_data} --shell $(which nologin) \
    --comment "puppetdb daemon"  puppetdb || :
fi
if rpm -q puppetdb | grep ^puppetdb-2.* > /dev/null && [ $1 -eq 2 ] ; then tar -czf /tmp/puppetdb-upgrade-config-files.tgz -C /etc/puppetdb/conf.d config.ini database.ini jetty.ini ; fi

%post
%{_app_prefix}/scripts/install.sh postinst_redhat
# Reload the systemd units
systemctl daemon-reload >/dev/null 2>&1 || :
%systemd_post puppetdb.service

%preun
%systemd_preun puppetdb.service

%postun
%systemd_postun_with_restart puppetdb.service

%files
%defattr(-, root, root)
%dir %attr(0700, puppetdb, puppetdb) %{_app_logdir}
%dir %attr(0750, puppetdb, puppetdb) %{_projconfdir}
%{_app_prefix}
%{_unitdir}/%{name}.service
%{_tmpfilesdir}/%{name}.conf
%config(noreplace) %{_projconfdir}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_app_bindir}/puppetdb
%{_ux_bindir}/puppetdb
%attr(-, puppetdb, puppetdb) %{_app_data}
%dir %attr(0755, puppetdb, puppetdb) %{_app_rundir}

%files termini
%defattr(-, root, root)
%{rubylibdir}/puppet/face/node/deactivate.rb
%{rubylibdir}/puppet/face/node/status.rb
%{rubylibdir}/puppet/functions/puppetdb_query.rb
%{rubylibdir}/puppet/indirector/catalog/puppetdb.rb
%{rubylibdir}/puppet/indirector/facts/puppetdb.rb
%{rubylibdir}/puppet/indirector/facts/puppetdb_apply.rb
%{rubylibdir}/puppet/indirector/node/puppetdb.rb
%{rubylibdir}/puppet/indirector/resource/puppetdb.rb
%{rubylibdir}/puppet/reports/puppetdb.rb
%{rubylibdir}/puppet/util/puppetdb.rb
%{rubylibdir}/puppet/util/puppetdb/atom.rb
%{rubylibdir}/puppet/util/puppetdb/char_encoding.rb
%{rubylibdir}/puppet/util/puppetdb/command.rb
%{rubylibdir}/puppet/util/puppetdb/command_names.rb
%{rubylibdir}/puppet/util/puppetdb/config.rb
%{rubylibdir}/puppet/util/puppetdb/http.rb


%changelog
* Thu Nov 01 2018 WellerNET <dev@wellernet.ch> - 5.2.6-1
- Build for 5.2.6
