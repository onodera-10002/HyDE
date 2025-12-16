import React, { useState, useRef, useEffect } from "react";
import {
  ChakraProvider,
  Box,
  VStack,
  HStack,
  Text,
  Input,
  Button,
  Card,
  CardBody,
  Heading,
  Badge,
  Spinner,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Link,
  Icon,
  Flex,
  Spacer,
} from "@chakra-ui/react";
import { FiSend, FiUpload, FiFileText, FiLink, FiCpu } from "react-icons/fi";
import axios from "axios";

// ==========================================
// 1. 型定義
// ==========================================

interface SourceItem {
  title: string | null;
  url: string;
  page: number | null;
}

interface AnswerItem {
  question: string;
  answer: string;
  sources: SourceItem[] | null;
}

interface ChatOutput {
  responses: AnswerItem[] | null;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceItem[];
}

// ==========================================
// 2. 設定 & APIクライアント
// ==========================================

const API_BASE_URL = "http://127.0.0.1:8005";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ==========================================
// 3. コンポーネント実装
// ==========================================

function App() {
  return (
    <ChakraProvider>
      {/* 画面全体を使用 - Flexレイアウト */}
      <Flex minH="100vh" h="100vh" bg="gray.100" direction="column">
        {/* ヘッダー部分 */}
        <Flex alignItems="center" px={8} py={4} bg="white" shadow="sm" borderBottom="1px solid" borderColor="gray.200">
          <Icon as={FiCpu} boxSize={8} color="teal.500" mr={3} />
          <Heading size="lg" color="gray.700">
            Aozora RAG Platform
          </Heading>
          <Spacer />
          <Badge colorScheme="teal" variant="subtle" fontSize="0.9em" px={3} py={1} borderRadius="full">
            Connected
          </Badge>
        </Flex>
        
        {/* メインエリア - 画面いっぱいに広げる */}
        <Flex flex="1" overflow="hidden">
          <Tabs variant="line" colorScheme="teal" isFitted w="100%" h="100%" display="flex" flexDirection="column">
            <TabList px={8} bg="white" borderBottom="2px solid" borderColor="gray.200">
              <Tab _selected={{ color: 'teal.500', borderColor: 'teal.500', fontWeight: 'bold' }} py={4}>
                <Icon as={FiFileText} mr={2} /> Chat Interface
              </Tab>
              <Tab _selected={{ color: 'teal.500', borderColor: 'teal.500', fontWeight: 'bold' }} py={4}>
                <Icon as={FiUpload} mr={2} /> Knowledge Base Upload
              </Tab>
            </TabList>

            <TabPanels flex="1" overflow="hidden" bg="gray.50">
              <TabPanel h="100%" p={0}>
                <ChatInterface />
              </TabPanel>
              <TabPanel h="100%" p={8} overflowY="auto">
                <UploadInterface />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Flex>
      </Flex>
    </ChakraProvider>
  );
}

// --- チャット画面コンポーネント ---
const ChatInterface = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 初回レンダリング時にウェルカムメッセージを表示
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        role: "assistant",
        content: "こんにちは。ドキュメントに基づいた質問にお答えします。何かお手伝いしましょうか？"
      }]);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userQuestion = input;
    setInput("");
    
    setMessages((prev) => [...prev, { role: "user", content: userQuestion }]);
    setIsLoading(true);

    try {
      const res = await apiClient.post<ChatOutput>("/chat/", {
        questions: [userQuestion],
      });

      const responses = res.data.responses;

      if (responses && responses.length > 0) {
        const aiResponse = responses[0];
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: aiResponse.answer,
            sources: aiResponse.sources || [],
          },
        ]);
      } else {
        throw new Error("No response");
      }
    } catch (error) {
      console.error(error);
      toast({
        title: "Connection Error",
        description: "AIサーバーとの通信に失敗しました。",
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "top-right"
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "エラーが発生しました。サーバーの状態を確認してください。" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Flex direction="column" h="100%">
      {/* メッセージ表示エリア (高さを確保してスクロール) */}
      <Flex flex={1} overflowY="auto" bg="gray.50" px={8} py={6} direction="column">
        <VStack spacing={6} align="stretch" maxW="1200px" mx="auto">
          {messages.map((msg, idx) => (
            <Flex
              key={idx}
              alignSelf={msg.role === "user" ? "flex-end" : "flex-start"}
              w="100%"
              direction="column"
              align={msg.role === "user" ? "flex-end" : "flex-start"}
            >
              <Flex
                bg={msg.role === "user" ? "teal.500" : "white"}
                color={msg.role === "user" ? "white" : "gray.800"}
                px={6}
                py={4}
                borderRadius="2xl"
                borderBottomRightRadius={msg.role === "user" ? "sm" : "2xl"}
                borderBottomLeftRadius={msg.role === "assistant" ? "sm" : "2xl"}
                shadow={msg.role === "assistant" ? "md" : "sm"}
                maxW="85%"
              >
                <Text fontSize="md" lineHeight="1.6" whiteSpace="pre-wrap">
                  {msg.content}
                </Text>
              </Flex>

              {msg.role === "assistant" && msg.sources && msg.sources.length > 0 && (
                <Box mt={3} ml={2} maxW="85%">
                  <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={2} textTransform="uppercase" letterSpacing="wide">
                    Reference Sources
                  </Text>
                  <Flex wrap="wrap" gap={2}>
                    {msg.sources.map((src, i) => (
                      <Link 
                        key={i} 
                        href={src.url} 
                        isExternal 
                        _hover={{ textDecoration: 'none' }}
                      >
                        <Badge 
                          colorScheme="gray" 
                          variant="solid" 
                          px={3} 
                          py={1} 
                          borderRadius="full" 
                          cursor="pointer"
                          display="flex"
                          alignItems="center"
                          _hover={{ bg: "gray.300" }}
                        >
                          <Icon as={FiLink} mr={1} />
                          {src.title || "Document"} (p.{src.page})
                        </Badge>
                      </Link>
                    ))}
                  </Flex>
                </Box>
              )}
            </Flex>
          ))}
          {isLoading && (
            <Flex alignSelf="flex-start" bg="white" px={6} py={4} borderRadius="2xl" shadow="md">
              <HStack spacing={3}>
                <Spinner size="sm" color="teal.500" />
                <Text fontSize="sm" color="gray.500">Thinking...</Text>
              </HStack>
            </Flex>
          )}
          <div ref={messagesEndRef} />
        </VStack>
      </Flex>

      {/* 入力エリア */}
      <Flex p={6} bg="white" borderTop="1px solid" borderColor="gray.200" justify="center">
        <HStack maxW="1200px" w="100%" spacing={4}>
          <Input
            placeholder="ここに質問を入力してください..."
            size="lg"
            fontSize="md"
            borderRadius="full"
            bg="gray.50"
            border="2px solid"
            borderColor="transparent"
            _focus={{ bg: "white", borderColor: "teal.500" }}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            disabled={isLoading}
            boxShadow="inner"
          />
          <Button
            size="lg"
            colorScheme="teal"
            borderRadius="full"
            px={8}
            onClick={handleSend}
            isLoading={isLoading}
            leftIcon={<FiSend />}
            boxShadow="md"
            _hover={{ transform: 'translateY(-2px)', boxShadow: 'lg' }}
          >
            Send
          </Button>
        </HStack>
      </Flex>
    </Flex>
  );
};

// --- アップロード画面 ---
const UploadInterface = () => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const toast = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !title) {
      toast({
        title: "Missing Information",
        description: "ファイルとタイトルを入力してください。",
        status: "warning",
      });
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);

    try {
      const res = await apiClient.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      toast({
        title: "Upload Successful",
        description: `${res.data.processed_pages} ページをデータベースに登録しました。`,
        status: "success",
        duration: 5000,
        isClosable: true,
      });
      
      setFile(null);
      setTitle("");
    } catch (error) {
      console.error("Upload error:", error);
      toast({
        title: "Upload Failed",
        description: "サーバーエラーが発生しました。",
        status: "error",
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Box maxW="1000px" mx="auto" h="100%">
      <VStack spacing={8} w="100%" h="100%" justify="center">
        <VStack spacing={2} textAlign="center">
          <Heading size="lg" color="gray.700">Add Knowledge</Heading>
          <Text color="gray.500">AIに新しいドキュメント（PDF/テキスト）を学習させます。</Text>
        </VStack>

        <Card variant="outline" w="100%" bg="white" shadow="sm" borderRadius="xl">
          <CardBody p={8}>
            <VStack spacing={6}>
              <Box w="100%">
                <Text mb={2} fontWeight="bold" color="gray.600">Document Title</Text>
                <Input 
                  placeholder="例: 2024年度 運用ガイドライン" 
                  size="lg"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </Box>

              <Box w="100%">
                <Text mb={2} fontWeight="bold" color="gray.600">File</Text>
                <Box 
                  border="2px dashed" 
                  borderColor="gray.300" 
                  borderRadius="lg" 
                  p={6} 
                  textAlign="center"
                  bg="gray.50"
                  _hover={{ borderColor: "teal.500", bg: "teal.50" }}
                  cursor="pointer"
                  onClick={() => document.getElementById('file-upload')?.click()}
                >
                  <VStack spacing={2}>
                    <Icon as={FiUpload} boxSize={8} color="gray.400" />
                    <Text fontSize="sm" color="gray.500">
                      {file ? file.name : "クリックしてファイルを選択"}
                    </Text>
                  </VStack>
                  <Input 
                    id="file-upload"
                    type="file" 
                    display="none"
                    onChange={handleFileChange} 
                    accept=".pdf,.txt,.md"
                  />
                </Box>
              </Box>

              <Button
                colorScheme="teal"
                size="lg"
                w="full"
                onClick={handleUpload}
                isLoading={isUploading}
                isDisabled={!file || !title}
                mt={4}
              >
                Upload Document
              </Button>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  );
};

export default App;
