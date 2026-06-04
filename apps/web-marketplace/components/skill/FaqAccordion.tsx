import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export interface FaqAccordionProps {
  faqMd: string | null;
}

/**
 * Splits ``faq_md`` into Q&A pairs.
 *
 * Convention: each ``##`` heading is a question; following text until the
 * next ``##`` is the answer. Forgiving fallback: if no headings are found,
 * the entire block becomes one "FAQ" item.
 */
function parseFaq(md: string): { question: string; answer: string }[] {
  const lines = md.split(/\r?\n/);
  const items: { question: string; answer: string }[] = [];
  let current: { question: string; answer: string[] } | null = null;
  for (const line of lines) {
    const m = /^##\s+(.*)$/.exec(line);
    if (m) {
      if (current) {
        items.push({ question: current.question, answer: current.answer.join("\n").trim() });
      }
      current = { question: (m[1] ?? "").trim(), answer: [] };
    } else if (current) {
      current.answer.push(line);
    }
  }
  if (current) {
    items.push({ question: current.question, answer: current.answer.join("\n").trim() });
  }
  if (items.length === 0 && md.trim()) {
    return [{ question: "FAQ", answer: md.trim() }];
  }
  return items;
}

export function FaqAccordion({ faqMd }: FaqAccordionProps) {
  if (!faqMd?.trim()) {
    return (
      <p className="text-sm text-fg-muted">
        No FAQ from this creator yet.
      </p>
    );
  }
  const items = parseFaq(faqMd);
  return (
    <Accordion type="single" collapsible className="w-full">
      {items.map((item, idx) => (
        <AccordionItem key={idx} value={`faq-${idx}`}>
          <AccordionTrigger>{item.question}</AccordionTrigger>
          <AccordionContent className="whitespace-pre-wrap text-sm text-fg-muted">
            {item.answer}
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
}
