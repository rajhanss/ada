import React, { useState } from 'react';
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
} from 'react-native';
import { ADA_THEME } from './src/theme';
import { HomeScreen } from './src/screens/HomeScreen';
import { TasksScreen } from './src/screens/TasksScreen';
import { ApprovalsScreen } from './src/screens/ApprovalsScreen';
import { DevicesScreen } from './src/screens/DevicesScreen';

type Tab = 'chat' | 'tasks' | 'approvals' | 'devices';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('chat');

  const renderScreen = () => {
    switch (activeTab) {
      case 'chat':
        return <HomeScreen />;
      case 'tasks':
        return <TasksScreen />;
      case 'approvals':
        return <ApprovalsScreen />;
      case 'devices':
        return <DevicesScreen />;
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor={ADA_THEME.colors.background} />

      {/* Main Screen Container */}
      <View style={styles.content}>{renderScreen()}</View>

      {/* Bottom Navigation Bar */}
      <View style={styles.navBar}>
        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setActiveTab('chat')}
        >
          <Text style={[styles.navText, activeTab === 'chat' && styles.activeNavText]}>
            💬 Chat
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setActiveTab('tasks')}
        >
          <Text style={[styles.navText, activeTab === 'tasks' && styles.activeNavText]}>
            📋 Tasks
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setActiveTab('approvals')}
        >
          <Text style={[styles.navText, activeTab === 'approvals' && styles.activeNavText]}>
            🛡️ Approvals
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setActiveTab('devices')}
        >
          <Text style={[styles.navText, activeTab === 'devices' && styles.activeNavText]}>
            💻 Devices
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: ADA_THEME.colors.background,
  },
  content: {
    flex: 1,
  },
  navBar: {
    flexDirection: 'row',
    height: 60,
    backgroundColor: ADA_THEME.colors.surface,
    borderTopWidth: 1,
    borderTopColor: ADA_THEME.colors.border,
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  navItem: {
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  navText: {
    color: ADA_THEME.colors.textMuted,
    fontSize: 12,
    fontWeight: '600',
  },
  activeNavText: {
    color: ADA_THEME.colors.primary,
    fontWeight: '700',
  },
});
