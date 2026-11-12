import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, FlatList, StyleSheet } from 'react-native';
import { ADA_THEME } from '../theme';
import { mobileApi } from '../api';
import type { ApprovalRequest } from '../../../shared/contracts/types';

export const ApprovalsScreen: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([
    {
      id: 'appr-mob-1',
      user_id: 'user',
      tool_name: 'delete_directory',
      tool_args: { path: 'C:\\Projects\\target\\debug' },
      risk_level: 'critical',
      reason: 'delete_directory requires explicit confirmation before removing files.',
      status: 'pending',
      created_at: new Date().toISOString(),
    },
  ]);

  useEffect(() => {
    mobileApi.listApprovals().then(setApprovals).catch(() => {});
  }, []);

  const handleAction = async (id: string, approved: boolean) => {
    try {
      await mobileApi.resolveApproval(id, approved);
    } catch {}
    setApprovals((prev) => prev.filter((a) => a.id !== id));
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Pending Authorizations</Text>
      <Text style={styles.subtitle}>
        Approve or reject high-risk actions requested on your computer.
      </Text>

      {approvals.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No pending actions require authorization.</Text>
        </View>
      ) : (
        <FlatList
          data={approvals}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.toolName}>{item.tool_name}</Text>
                <Text style={styles.riskBadge}>{item.risk_level.toUpperCase()}</Text>
              </View>

              <Text style={styles.reason}>{item.reason}</Text>

              <View style={styles.buttonRow}>
                <TouchableOpacity
                  style={[styles.btn, styles.approveBtn]}
                  onPress={() => handleAction(item.id, true)}
                >
                  <Text style={styles.btnText}>Approve</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.btn, styles.denyBtn]}
                  onPress={() => handleAction(item.id, false)}
                >
                  <Text style={styles.btnText}>Deny</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}
        />
      )}
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
    borderColor: ADA_THEME.colors.primary,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  toolName: {
    color: ADA_THEME.colors.textMain,
    fontSize: 16,
    fontWeight: '700',
  },
  riskBadge: {
    color: ADA_THEME.colors.warning,
    fontSize: 10,
    fontWeight: '800',
    backgroundColor: 'rgba(245, 158, 11, 0.2)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  reason: {
    color: ADA_THEME.colors.textMain,
    fontSize: 13,
    marginBottom: 16,
    lineHeight: 18,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
  },
  btn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  approveBtn: {
    backgroundColor: ADA_THEME.colors.success,
  },
  denyBtn: {
    backgroundColor: ADA_THEME.colors.danger,
  },
  btnText: {
    color: '#FFF',
    fontWeight: '700',
    fontSize: 13,
  },
  emptyContainer: {
    padding: 32,
    backgroundColor: ADA_THEME.colors.surface,
    borderRadius: 12,
    alignItems: 'center',
  },
  emptyText: {
    color: ADA_THEME.colors.textMuted,
    fontSize: 13,
  },
});
