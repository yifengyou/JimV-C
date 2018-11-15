INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('WindowsMode2', '用作 MS-Windows 系列的系统初始化。初始化操作依据 WindowsXP 来实现。', 1);

-- For WindowsXP
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (6, 1, 0, '/WINDOWS/jimv_init.bat', 'netsh interface ip set address name="Ethernet" source=static {IP} {NETMASK} {GATEWAY} 1
netsh interface ip set dns "Ethernet" static {DNS1} primary
netsh interface ip add dns "Ethernet" {DNS2}
wmic computersystem where name="%COMPUTERNAME%" call rename name="{HOSTNAME}"
net user Administrator {PASSWORD}
@ping 127.0.0.1 -n 3 > NUL
sc delete JimVInit
del C:\\WINDOWS\\jimv_init.bat
shutdown -r -t 0
@ping 127.0.0.1 -n 2 > NUL', '');

INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Windows-2016-Standard', 'Windows 2016 Standard。', 'windows', 'windows', 10, 0, 'x86_64', 'Windows Server 2016 Standard', 1, 'icon-os icon-os-windows', 5);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Windows-2008-R2-Enterprise', 'Windows 2008 R2 Enterprise。', 'windows', 'windows', 6, 1, 'x86_64', 'Windows Server 2008 R2 Enterprise', 1, 'icon-os icon-os-windows', 5);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Windows7-Ultimate-SP1', 'Windows7 Ultimate SP1 x64。', 'windows', 'windows', 6, 1, 'x86_64', 'Windows7 Ultimate SP1 x64', 1, 'icon-os icon-os-windows', 5);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Windows-2003-R2-Enterprise-SP2', 'Windows 2003 R2 Enterprise SP2 x64。', 'windows', 'windows', 5, 2, 'x86_64', 'Windows 2003 R2 Enterprise SP2', 1, 'icon-os icon-os-windows', 6);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('WindowsXP-SP3', 'WindowsXP SP1 x64。', 'windows', 'windows', 5, 1, 'x86', 'Windows XP SP3', 1, 'icon-os icon-os-windows', 6);