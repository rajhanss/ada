import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { ADA_THEME } from '../theme';
import { mobileApi } from '../api';
import type { Message } from '../../../shared/contracts/types';

export const HomeScreen: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'm1',
      conversation_id: 'c1',
      user_id: 'ada',
      role: 'assistant',
      content: 'ADA Mobile Companion online. Ready to coordinate tasks on your workstation or answer questions.',
      content_type: 'text',
      created_at: new Date().toISOString(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleSend = async () => {
    const text = inputText.trim();
    if (!text || isSending) return;

    setInputText('');
    setIsSending(true);

    const userMsg: Message = {
      id: `m_${Date.now()}`,
      conversation_id: 'c1',
      user_id: 'user',
      role: 'user',
      content: text,
      content_type: 'text',
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const resp = await mobileApi.sendMessage('c1', text);
      setMessages((prev) => [...prev, resp]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          conversation_id: 'c1',
          user_id: 'ada',
          role: 'assistant',
          content: `Action dispatched. Response: ${err.message}`,
          content_type: 'text',
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Target Workstation Header */}
      <View style={styles.header}>
        <View style={styles.devicePill}>
          <View style={styles.onlineDot} />
          <Text style={styles.deviceText}>Target: Windows Primary Workstation</Text>
        </View>
        <Text style={styles.autonomyBadge}>SUPERVISED</Text>
      </View>

      {/* Message Feed */}
      <FlatList
        data={messages}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.messageList}
        renderItem={({ item }) => {
          const isUser = item.role === 'user';
          return (
            <View
              style={[
                styles.messageBubble,
                isUser ? styles.userBubble : styles.adaBubble,
              ]}
            >
              <Text style={styles.roleLabel}>{isUser ? 'You' : 'ADA'}</Text>
              <Text style={styles.messageContent}>{item.content}</Text>
            </View>
          );
        }}
      />

      {/* Input Row */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Command ADA on your laptop..."
          placeholderTextColor={ADA_THEME.colors.textDim}
        />
        <TouchableOpacity
          style={[styles.sendButton, !inputText.trim() && styles.disabledButton]}
          onPress={handleSend}
          disabled={!inputText.trim() || isSending}
        >
          {isSending ? (
            <ActivityIndicator size="small" color="#FFF" />
          ) : (
            <Text style={styles.sendButtonText}>Send</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: ADA_THEME.colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: ADA_THEME.colors.border,
    backgroundColor: ADA_THEME.colors.surface,
  },
  devicePill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: ADA_THEME.colors.success,
  },
  deviceText: {
    color: ADA_THEME.colors.textMain,
    fontSize: 12,
    fontWeight: '600',
  },
  autonomyBadge: {
    color: ADA_THEME.colors.primary,
    fontSize: 10,
    fontWeight: '700',
    backgroundColor: ADA_THEME.colors.primaryGlow,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  messageList: {
    padding: 16,
    gap: 12,
  },
  messageBubble: {
    padding: 14,
    borderRadius: 12,
    maxWidth: '82%',
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#23232C',
    borderWidth: 1,
    borderColor: '#363644',
  },
  adaBubble: {
    alignSelf: 'flex-start',
    backgroundColor: ADA_THEME.colors.surface,
    borderWidth: 1,
    borderColor: ADA_THEME.colors.border,
  },
  roleLabel: {
    color: ADA_THEME.colors.primary,
    fontSize: 11,
    fontWeight: '700',
    marginBottom: 4,
  },
  messageContent: {
    color: ADA_THEME.colors.textMain,
    fontSize: 14,
    lineHeight: 20,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: ADA_THEME.colors.surface,
    borderTopWidth: 1,
    borderTopColor: ADA_THEME.colors.border,
    gap: 8,
  },
  textInput: {
    flex: 1,
    backgroundColor: ADA_THEME.colors.background,
    color: ADA_THEME.colors.textMain,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 8,
    fontSize: 14,
    borderWidth: 1,
    borderColor: ADA_THEME.colors.border,
  },
  sendButton: {
    backgroundColor: ADA_THEME.colors.primary,
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  disabledButton: {
    backgroundColor: ADA_THEME.colors.border,
  },
  sendButtonText: {
    color: '#FFF',
    fontWeight: '700',
    fontSize: 13,
  },
});
