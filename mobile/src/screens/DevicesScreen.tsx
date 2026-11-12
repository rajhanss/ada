import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { ADA_THEME } from '../theme';
import { mobileApi } from '../api';
import type { Device } from '../../../shared/contracts/types';

export const DevicesScreen: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([
    {
      id: 'd-win-1',
      user_id: 'user',
      device_type: 'desktop',
      display_name: 'Windows Primary Workstation',
      platform: 'windows',
      capabilities: ['shell', 'files', 'screen', 'automation'],
      is_online: true,
      created_at: new Date().toISOString(),
    },
    {
      id: 'd-mob-1',
      user_id: 'user',
      device_type: 'mobile',
      display_name: 'This Phone (Mobile Companion)',
      platform: 'android',
      capabilities: ['voice', 'remote_dispatch', 'push_auth'],
      is_online: true,
      created_at: new Date().toISOString(),
    },
  ]);

  useEffect(() => {
    mobileApi.listDevices().then(setDevices).catch(() => {});
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Connected Ecosystem</Text>
      <Text style={styles.subtitle}>Endpoints linked to your unified intelligence</Text>

      <FlatList
        data={devices}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.devName}>{item.display_name}</Text>
              <View style={styles.onlineTag}>
                <View style={styles.onlineDot} />
                <Text style={styles.onlineText}>ONLINE</Text>
              </View>
            </View>

            <Text style={styles.platform}>Platform: {item.platform.toUpperCase()}</Text>

            <View style={styles.capsContainer}>
              {item.capabilities.map((c) => (
                <Text key={c} style={styles.capTag}>
                  {c}
                </Text>
              ))}
            </View>
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
  },
  subtitle: {
    color: ADA_THEME.colors.textMuted,
    fontSize: 13,
    marginBottom: 16,
    marginTop: 4,
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
  devName: {
    color: ADA_THEME.colors.textMain,
    fontSize: 15,
    fontWeight: '600',
  },
  onlineTag: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  onlineDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: ADA_THEME.colors.success,
  },
  onlineText: {
    color: ADA_THEME.colors.success,
    fontSize: 10,
    fontWeight: '700',
  },
  platform: {
    color: ADA_THEME.colors.textMuted,
    fontSize: 12,
    marginBottom: 10,
  },
  capsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  capTag: {
    backgroundColor: ADA_THEME.colors.surfaceHover,
    color: ADA_THEME.colors.primary,
    fontSize: 10,
    fontWeight: '600',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
});
