import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { ADA_THEME } from '../theme';
import { mobileApi } from '../api';
import type { Task } from '../../../shared/contracts/types';

export const TasksScreen: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: 'mob-task-1',
      user_id: 'user',
      title: 'Inspect repository status',
      description: 'Run git status on laptop',
      tool_name: 'run_dev_command',
      tool_args: { command: 'git status' },
      priority: 5,
      status: 'completed',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'mob-task-2',
      user_id: 'user',
      title: 'Run test suite',
      description: 'Execute unit tests via pytest',
      tool_name: 'run_dev_command',
      tool_args: { command: 'pytest tests/' },
      priority: 5,
      status: 'running',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ]);

  useEffect(() => {
    mobileApi.listTasks().then(setTasks).catch(() => {});
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Workstation Tasks</Text>
      <FlatList
        data={tasks}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.taskTitle}>{item.title}</Text>
              <Text
                style={[
                  styles.statusBadge,
                  item.status === 'completed'
                    ? styles.statusCompleted
                    : styles.statusRunning,
                ]}
              >
                {item.status.toUpperCase()}
              </Text>
            </View>
            <Text style={styles.toolName}>Tool: {item.tool_name}</Text>
            <Text style={styles.desc}>{item.description}</Text>
          </View>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: ADA_THEME.colors.background,
    padding: 16,
  },
  title: {
    color: ADA_THEME.colors.textMain,
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 16,
  },
  list: {
    gap: 12,
  },
  card: {
    backgroundColor: ADA_THEME.colors.surface,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: ADA_THEME.colors.border,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  taskTitle: {
    color: ADA_THEME.colors.textMain,
    fontSize: 15,
    fontWeight: '600',
    flex: 1,
  },
  statusBadge: {
    fontSize: 10,
    fontWeight: '700',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  statusCompleted: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    color: ADA_THEME.colors.success,
  },
  statusRunning: {
    backgroundColor: ADA_THEME.colors.primaryGlow,
    color: ADA_THEME.colors.primary,
  },
  toolName: {
    color: ADA_THEME.colors.primary,
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 4,
  },
  desc: {
    color: ADA_THEME.colors.textMuted,
    fontSize: 13,
  },
});
