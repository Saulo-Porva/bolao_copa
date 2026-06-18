# Mobile UX

## Contexto de Uso do Motorista

Diferente de um usuário de escritório, o motorista usa o app em condições adversas:

| Condição | Impacto no design |
|----------|------------------|
| Luvas de trabalho | Touch targets ≥ 56px, evitar gestos complexos |
| Luz solar direta | Contraste mínimo 7:1 (WCAG AAA) |
| Vibração do veículo | Sem gestos que exijam precisão de pixel |
| Uma mão ocupada | Interface operável com uma mão |
| Pressa/stress | Fluxo principal em ≤ 3 taps, confirmações rápidas |
| Sinal instável | Feedback de offline, não travar em carregamento |

## Thumb-Friendly Design

**Zones de alcance** para celular com uma mão (polegar direito):

```
Parte superior = difícil (stretch zone)
Parte central  = alcançável (reachable zone)  
Parte inferior = fácil (natural zone) ← ações críticas aqui
```

**Regra do polegar:**
- Botão primário (Nova Viagem) → zona inferior
- Navegação principal → BottomNav (não header)
- Confirmações → bottom sheet (não modal centralizado)
- Ações destrutivas → fora da thumb zone ou com confirmação

## Gesture Patterns

**Suportados nativamente (sem implementação extra):**
- Tap: ação principal
- Long press: ações secundárias (cuidado — não óbvio)
- Swipe: navegação entre tabs/seções

**Evitar neste app:**
- Pinch/zoom (formulários não precisam)
- Gestos multi-toque
- Drag and drop (complexo com luvas)

## Estados de Conectividade

```tsx
// Hook para detectar conectividade
export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(
    typeof window !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}
```

**UX para offline:**
- Banner de aviso não intrusivo (topo, âmbar)
- Desabilitar botões de submit com mensagem clara
- Cache de dados de leitura (clientes, caminhões) no localStorage
- Não mostrar spinner infinito — timeout com mensagem

## PWA UX Considerations

### Instalação
- O banner de instalação do navegador aparece automaticamente
- Não bloquear o fluxo principal para mostrar prompt de instalação
- Após instalação: splash screen com logo PR Trasporti

### manifest.json — Configuração de Aparência

```json
{
  "name": "PR Trasporti — Rapportini",
  "short_name": "Rapportini",
  "theme_color": "#C0392B",
  "background_color": "#ffffff",
  "display": "standalone",
  "orientation": "portrait",
  "start_url": "/motorista/dashboard"
}
```

### Status Bar em iOS/Android
Com `display: standalone`, a status bar fica visível. Garantir que o header vermelho não conflita com a status bar escura do sistema.

## Loading States por Contexto

| Contexto | Pattern | Por quê |
|---------|---------|---------|
| Carregamento inicial da página | Skeleton screen | Evita flash de conteúdo vazio |
| Submit de formulário | Spinner no botão + desabilitar | Evita double-submit |
| Navegação entre páginas | Sem loader (Next.js é rápido) | Não adicionar latência visual |
| Busca/filtro | Debounce + spinner inline | Não bloquear input |

## Notificações e Alertas

**No contexto deste app, não usar:**
- Push notifications (complexidade, LGPD)
- Modais que bloqueiam a tela inteira

**Usar:**
- Toast/snackbar para feedback de ações (3s auto-dismiss para sucesso)
- Banner inline para erros persistentes (com botão de dismissal)
- Bottom sheet para confirmações importantes
