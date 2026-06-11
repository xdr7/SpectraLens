import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_state.dart';
import '../utils/constants.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: Consumer<AppState>(
        builder: (context, state, _) {
          return ListView(
            padding: const EdgeInsets.all(AppDimensions.paddingMedium),
            children: [
              // Scan Settings
              _buildSectionHeader('Scan Settings'),
              const SizedBox(height: 8),
              Card(
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.timer, color: AppColors.primary),
                      title: const Text(
                        'Scan Interval',
                        style: TextStyle(color: AppColors.textPrimary),
                      ),
                      subtitle: Text(
                        '${state.scanInterval} seconds',
                        style: const TextStyle(color: AppColors.textSecondary),
                      ),
                      trailing: SizedBox(
                        width: 200,
                        child: Slider(
                          value: state.scanInterval.toDouble(),
                          min: 1,
                          max: 30,
                          divisions: 29,
                          activeColor: AppColors.primary,
                          inactiveColor: Colors.white.withOpacity(0.1),
                          label: '${state.scanInterval}s',
                          onChanged: (value) => state.setScanInterval(value.toInt()),
                        ),
                      ),
                    ),
                    const Divider(height: 1, color: Colors.white10),
                    SwitchListTile(
                      secondary: const Icon(Icons.wifi_protected_setup, color: AppColors.secondary),
                      title: const Text(
                        'Auto-scan on startup',
                        style: TextStyle(color: AppColors.textPrimary),
                      ),
                      subtitle: const Text(
                        'Automatically start scanning when app opens',
                        style: TextStyle(color: AppColors.textSecondary),
                      ),
                      value: true,
                      activeColor: AppColors.primary,
                      onChanged: (value) {},
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Display Settings
              _buildSectionHeader('Display Settings'),
              const SizedBox(height: 8),
              Card(
                child: Column(
                  children: [
                    SwitchListTile(
                      secondary: const Icon(Icons.dark_mode, color: AppColors.warning),
                      title: const Text(
                        'Dark Mode',
                        style: TextStyle(color: AppColors.textPrimary),
                      ),
                      subtitle: const Text(
                        'Use dark color theme',
                        style: TextStyle(color: AppColors.textSecondary),
                      ),
                      value: state.isDarkMode,
                      activeColor: AppColors.primary,
                      onChanged: (value) => state.toggleDarkMode(),
                    ),
                    const Divider(height: 1, color: Colors.white10),
                    ListTile(
                      leading: const Icon(Icons.palette, color: AppColors.accent),
                      title: const Text(
                        'Theme Color',
                        style: TextStyle(color: AppColors.textPrimary),
                      ),
                      subtitle: const Text(
                        'Cyan',
                        style: TextStyle(color: AppColors.textSecondary),
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          _buildColorDot(AppColors.primary),
                          const SizedBox(width: 8),
                          _buildColorDot(AppColors.secondary),
                          const SizedBox(width: 8),
                          _buildColorDot(AppColors.success),
                          const SizedBox(width: 8),
                          _buildColorDot(AppColors.error),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Data Settings
              _buildSectionHeader('Data Management'),
              const SizedBox(height: 8),
              Card(
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.storage, color: AppColors.success),
                      title: const Text(
                        'Storage Location',
                        style: TextStyle(color: AppColors.textPrimary),
                      ),
                      subtitle: const Text(
                        'App data directory',
                        style: TextStyle(color: AppColors.textSecondary),
                      ),
                      trailing: const Icon(Icons.chevron_right, color: AppColors.textSecondary),
                      onTap: () {},
                    ),
                    const Divider(height: 1, color: Colors.white10),
                    ListTile(
                      leading: const Icon(Icons.delete_sweep, color: AppColors.error),
                      title: const Text(
                        'Clear All Data',
                        style: TextStyle(color: AppColors.error),
                      ),
                      subtitle: const Text(
                        'Remove all measurements and scan history',
                        style: TextStyle(color: AppColors.textSecondary),
                      ),
                      onTap: () => _showClearDataDialog(context, state),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // About
              _buildSectionHeader('About'),
              const SizedBox(height: 8),
              Card(
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.info, color: AppColors.primary),
                      title: const Text(
                        'Version',
                        style: TextStyle(color: AppColors.textPrimary),
                      ),
                      subtitle: const Text(
                        AppStrings.version,
                        style: TextStyle(color: AppColors.textSecondary),
                      ),
                    ),
                    const Divider(height: 1, color: Colors.white10),
                    ListTile(
                      leading: const Icon(Icons.code, color: AppColors.secondary),
                      title: const Text(
                        'Developer',
                        style: TextStyle(color: AppColors.textPrimary),
                      ),
                      subtitle: const Text(
                        'SpectraLens Team',
                        style: TextStyle(color: AppColors.textSecondary),
                      ),
                    ),
                    const Divider(height: 1, color: Colors.white10),
                    ListTile(
                      leading: const Icon(Icons.description, color: AppColors.accent),
                      title: const Text(
                        'License',
                        style: TextStyle(color: AppColors.textPrimary),
                      ),
                      subtitle: const Text(
                        'MIT License',
                        style: TextStyle(color: AppColors.textSecondary),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),

              // Footer
              Center(
                child: Text(
                  AppStrings.tagline,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.3),
                    fontSize: 12,
                    fontStyle: FontStyle.italic,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              const SizedBox(height: 16),
            ],
          );
        },
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: AppColors.textSecondary,
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  Widget _buildColorDot(Color color) {
    return Container(
      width: 24,
      height: 24,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        border: Border.all(color: Colors.white24, width: 2),
      ),
    );
  }

  void _showClearDataDialog(BuildContext context, AppState state) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: const Text(
          'Clear All Data?',
          style: TextStyle(color: AppColors.textPrimary),
        ),
        content: const Text(
          'This will permanently delete all measurements, scan history, and collected data. This action cannot be undone.',
          style: TextStyle(color: AppColors.textSecondary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              state.clearData();
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('All data cleared')),
              );
            },
            child: const Text(
              'Clear',
              style: TextStyle(color: AppColors.error),
            ),
          ),
        ],
      ),
    );
  }
}
