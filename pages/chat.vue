<template>
    <div class="d-flex flex-column fill-height">
        <div class="flex-shrink-0 pa-4 pb-2">
            <div class="d-flex align-center ga-3">
                <v-icon>mdi-robot</v-icon>
                <h1 class="text-h5" style="font-family: var(--font-headline); font-weight: 400">
                    Company Analyst
                </h1>
                <v-spacer />
                <v-select
                    v-if="agents.length > 1"
                    v-model="selectedAgentId"
                    :items="agents"
                    item-title="display_name"
                    item-value="engine_id"
                    label="Agent"
                    density="compact"
                    style="max-width: 240px"
                    hide-details
                />
                <v-btn
                    v-if="hasMessages"
                    icon
                    variant="text"
                    size="small"
                    @click="clearChat"
                    title="Clear chat"
                >
                    <v-icon>mdi-delete-outline</v-icon>
                </v-btn>
            </div>
        </div>

        <v-divider />

        <div ref="messagesContainer" class="flex-grow-1 overflow-y-auto pa-4">
            <template v-if="!agents.length && !agentsLoading">
                <v-empty-state
                    headline="No agents deployed"
                    text="Deploy the company_analyst agent to enable AI analysis. Push to main and use /deploy_agent in Cursor."
                    icon="mdi-robot-off"
                />
            </template>

            <template v-else-if="!hasMessages">
                <div class="d-flex flex-column align-center justify-center fill-height">
                    <v-icon size="64" color="primary" class="mb-4" style="opacity: 0.3">
                        mdi-chat-processing-outline
                    </v-icon>
                    <p class="text-body-1" style="color: var(--lv-silver)">
                        Ask about Apple or Tesla financials, filings, or comparisons
                    </p>
                    <div class="d-flex flex-wrap ga-2 mt-4 justify-center">
                        <v-chip
                            v-for="prompt in samplePrompts"
                            :key="prompt"
                            variant="tonal"
                            @click="sendMessage(prompt)"
                        >
                            {{ prompt }}
                        </v-chip>
                    </div>
                </div>
            </template>

            <div v-for="msg in messages" :key="msg.id" class="mb-3">
                <div :class="['chat-bubble', msg.role === 'user' ? 'user-bubble' : 'agent-bubble']">
                    <div class="chat-role">{{ msg.role === 'user' ? 'You' : 'Analyst' }}</div>
                    <div class="chat-text" v-text="msg.text || (msg.streaming ? '...' : '')" />
                </div>
            </div>
        </div>

        <v-divider />

        <div class="flex-shrink-0 pa-4">
            <v-text-field
                v-model="inputText"
                placeholder="Ask about Apple or Tesla..."
                variant="outlined"
                hide-details
                :loading="chatLoading"
                :disabled="!agents.length"
                @keyup.enter="onSend"
            >
                <template v-slot:append-inner>
                    <v-btn
                        icon
                        variant="text"
                        size="small"
                        :disabled="!inputText.trim() || chatLoading"
                        @click="onSend"
                    >
                        <v-icon>mdi-send</v-icon>
                    </v-btn>
                </template>
            </v-text-field>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { useAgentChat } from '~/composables/useAgentChat';
    import { useTenantConfig } from '~/composables/useTenantConfig';

    const { config, fetchConfig } = useTenantConfig();
    const {
        messages,
        loading: chatLoading,
        hasMessages,
        selectAgent,
        sendMessage,
        clearChat,
    } = useAgentChat();

    const inputText = ref('');
    const messagesContainer = ref<HTMLElement | null>(null);
    const agentsLoading = ref(true);
    const selectedAgentId = ref<string | null>(null);

    const agents = computed(() => config.value?.agents ?? []);

    const samplePrompts = [
        'Compare Apple and Tesla revenue trends',
        "What are Apple's latest financials?",
        "Show Tesla's recent SEC filings",
        'Which company has more debt?',
    ];

    watch(selectedAgentId, (id) => {
        if (id) selectAgent(id);
    });

    watch(messages, () => {
        nextTick(() => {
            if (messagesContainer.value) {
                messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
            }
        });
    });

    function onSend() {
        if (!inputText.value.trim()) return;
        sendMessage(inputText.value);
        inputText.value = '';
    }

    onMounted(async () => {
        try {
            await fetchConfig();
            const agentList = config.value?.agents ?? [];
            if (agentList.length > 0) {
                selectedAgentId.value = agentList[0].engine_id;
                selectAgent(agentList[0].engine_id);
            }
        } catch {
            // no agents available
        } finally {
            agentsLoading.value = false;
        }
    });
</script>

<style scoped>
    .chat-bubble {
        max-width: 80%;
        padding: 10px 14px;
        border-radius: 12px;
    }

    .user-bubble {
        margin-left: auto;
        background: rgba(63, 234, 0, 0.1);
        border: 1px solid rgba(63, 234, 0, 0.2);
    }

    .agent-bubble {
        margin-right: auto;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .chat-role {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--lv-silver);
        margin-bottom: 4px;
    }

    .chat-text {
        white-space: pre-wrap;
        line-height: 1.5;
    }
</style>
