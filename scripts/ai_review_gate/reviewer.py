"""
Code Reviewer - AI-powered code review engine using Anthropic Claude.

Performs comprehensive code review for safety, clarity, and maintainability.
"""

import logging
import os
import json
import time
from typing import List, Dict, Optional, Any
from anthropic import Anthropic

from .types import (
    PRChanges,
    Finding,
    LLMAnalysis,
    FileChange,
    Violation,
    Category,
    Severity,
)
from .rules import RulesEngine
from .diff_gen import DiffGenerator

logger = logging.getLogger(__name__)


class CodeReviewer:
    """
    AI-powered code reviewer using Claude Sonnet 4.5.

    Combines pattern-based rule checking with LLM analysis for comprehensive review.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        strict_mode: bool = False,
    ):
        """
        Initialize code reviewer.

        Args:
            api_key: Anthropic API key (reads from env if not provided)
            model: Claude model to use
            strict_mode: If True, warnings also fail the build
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.strict_mode = strict_mode

        self.rules_engine = RulesEngine()
        self.diff_generator = DiffGenerator()

        logger.info(f"Initialized CodeReviewer with model: {model}")

    def review_changes(self, changes: PRChanges) -> List[Finding]:
        """
        Review all changes in the PR.

        Args:
            changes: PR changes to review

        Returns:
            List of findings
        """
        logger.info(f"Starting review of PR #{changes.pr_number}")
        all_findings = []

        for file_change in changes.files:
            # Skip removed files
            if file_change.status == "removed":
                continue

            # Skip files without patches
            if not file_change.patch:
                logger.warning(f"Skipping {file_change.filename}: no patch available")
                continue

            logger.info(f"Reviewing {file_change.filename}")
            findings = self.review_file(file_change, changes)
            all_findings.extend(findings)

        logger.info(f"Review complete: {len(all_findings)} findings")
        return all_findings

    def review_file(
        self, file_change: FileChange, pr_context: PRChanges
    ) -> List[Finding]:
        """
        Review a single file change.

        Args:
            file_change: File to review
            pr_context: Full PR context

        Returns:
            List of findings for this file
        """
        findings = []

        # Extract changed code from patch
        changed_code = self._extract_changed_code(file_change.patch)

        # Step 1: Apply pattern-based rules
        violations = self.rules_engine.check_all_rules(
            changed_code, file_change.filename
        )

        # Step 2: Enhance with LLM analysis
        llm_findings = self._analyze_with_llm(
            file_change, changed_code, pr_context
        )

        # Step 3: Merge pattern-based violations with LLM findings
        for violation in violations:
            explanation = self.rules_engine.explain_violation(violation)

            # Generate suggested fix
            suggested_fix = self.diff_generator.generate_fix_for_violation(
                violation, violation.rule_id, changed_code
            )

            finding = Finding(
                id=f"{violation.rule_id}_{file_change.filename}_{violation.line_start}",
                rule_id=violation.rule_id,
                category=Category.SAFETY if "SEC" in violation.rule_id else Category.CLARITY,
                severity=Severity.CRITICAL if "SEC" in violation.rule_id else Severity.WARNING,
                title=explanation.get("title", "Unknown Issue"),
                description=explanation.get("description", ""),
                explanation=explanation.get("why_matters", ""),
                violation=violation,
                suggested_fix=suggested_fix,
                documentation_url=explanation.get("learn_more"),
            )
            findings.append(finding)

        # Add LLM-discovered findings
        findings.extend(llm_findings)

        return findings

    def _extract_changed_code(self, patch: str) -> str:
        """
        Extract the actual code changes from a unified diff patch.

        Args:
            patch: Unified diff patch

        Returns:
            Changed code lines
        """
        lines = patch.split("\n")
        code_lines = []

        for line in lines:
            if line.startswith("+") and not line.startswith("+++"):
                # Added line (remove + prefix)
                code_lines.append(line[1:])
            elif line.startswith(" "):
                # Context line
                code_lines.append(line[1:])

        return "\n".join(code_lines)

    def _analyze_with_llm(
        self, file_change: FileChange, changed_code: str, pr_context: PRChanges
    ) -> List[Finding]:
        """
        Analyze code using Claude LLM for advanced detection.

        Args:
            file_change: File being analyzed
            changed_code: Changed code content
            pr_context: Full PR context

        Returns:
            List of LLM-discovered findings
        """
        # Build review prompt
        prompt = self._build_review_prompt(file_change, changed_code, pr_context)

        try:
            start_time = time.time()

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.2,  # Low temperature for consistent analysis
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            latency = time.time() - start_time

            # Parse response
            analysis = self._parse_llm_response(message, file_change)
            logger.info(
                f"LLM analysis complete: {len(analysis.findings)} findings "
                f"(confidence: {analysis.confidence:.2f}, latency: {latency:.2f}s)"
            )

            # Convert to Finding objects
            findings = self._convert_llm_findings(analysis, file_change)
            return findings

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}", exc_info=True)
            return []

    def _build_review_prompt(
        self, file_change: FileChange, changed_code: str, pr_context: PRChanges
    ) -> str:
        """
        Build comprehensive review prompt for Claude.

        Args:
            file_change: File being reviewed
            changed_code: Code changes
            pr_context: PR context

        Returns:
            Review prompt
        """
        prompt = f"""You are a senior software engineer performing a code review.

**PR Context:**
- Title: {pr_context.title}
- Author: {pr_context.author}
- Files changed: {pr_context.file_count}

**File Being Reviewed:**
- Path: {file_change.filename}
- Status: {file_change.status}
- Lines added: {file_change.additions}
- Lines removed: {file_change.deletions}

**Code Changes:**
```
{changed_code}
```

**Review Instructions:**

1. **Safety (Critical)**: Look for:
   - Security vulnerabilities (SQL injection, XSS, command injection)
   - Hardcoded credentials or secrets
   - Insecure deserialization
   - Path traversal risks
   - Missing input validation
   - Unsafe cryptography

2. **Clarity (Warning)**: Look for:
   - Unclear variable/function names
   - Missing or inadequate docstrings
   - Complex logic without explanation
   - Magic numbers without constants
   - Missing type hints

3. **Maintainability (Warning)**: Look for:
   - Code duplication
   - High complexity (deeply nested, long functions)
   - Tight coupling
   - Missing error handling
   - Inconsistent style

**Output Format:**
Respond with a JSON object:
```json
{{
  "findings": [
    {{
      "rule_id": "LLM001",
      "category": "safety|clarity|maintainability",
      "severity": "critical|warning|info",
      "title": "Short title",
      "description": "What's wrong",
      "explanation": "Why it matters",
      "line_start": 10,
      "line_end": 12,
      "code_snippet": "problematic code",
      "suggested_fix": "improved code",
      "confidence": 0.95
    }}
  ],
  "overall_confidence": 0.9,
  "reasoning": "Brief explanation of analysis approach"
}}
```

**Important:**
- Only report issues you're confident about (>0.7 confidence)
- Be specific about line numbers
- Provide actionable fix suggestions
- If no issues found, return empty findings array
"""
        return prompt

    def _parse_llm_response(
        self, message: Any, file_change: FileChange
    ) -> LLMAnalysis:
        """
        Parse Claude's response into structured analysis.

        Args:
            message: Claude API response
            file_change: File being analyzed

        Returns:
            Structured LLM analysis
        """
        try:
            # Extract text content
            content = message.content[0].text

            # Parse JSON response
            # Look for JSON block in markdown code fence
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                json_str = content

            data = json.loads(json_str)

            # Extract token usage
            token_usage = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }

            return LLMAnalysis(
                findings=data.get("findings", []),
                confidence=data.get("overall_confidence", 0.8),
                reasoning=data.get("reasoning", ""),
                token_usage=token_usage,
                latency=0.0,  # Set by caller
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Return empty analysis
            return LLMAnalysis(
                findings=[],
                confidence=0.0,
                reasoning="Failed to parse LLM response",
                token_usage={},
                latency=0.0,
            )

    def _convert_llm_findings(
        self, analysis: LLMAnalysis, file_change: FileChange
    ) -> List[Finding]:
        """
        Convert LLM analysis findings to Finding objects.

        Args:
            analysis: LLM analysis result
            file_change: File being analyzed

        Returns:
            List of Finding objects
        """
        findings = []

        for idx, llm_finding in enumerate(analysis.findings):
            # Skip low-confidence findings
            if llm_finding.get("confidence", 0) < 0.7:
                logger.debug(
                    f"Skipping low-confidence finding: {llm_finding.get('title')}"
                )
                continue

            # Map severity
            severity_str = llm_finding.get("severity", "warning")
            severity = Severity(severity_str)

            # Map category
            category_str = llm_finding.get("category", "maintainability")
            category = Category(category_str)

            # Create violation
            violation = Violation(
                rule_id=llm_finding.get("rule_id", f"LLM{idx:03d}"),
                file_path=file_change.filename,
                line_start=llm_finding.get("line_start", 1),
                line_end=llm_finding.get("line_end", 1),
                message=llm_finding.get("description", ""),
                code_snippet=llm_finding.get("code_snippet", ""),
            )

            # Generate diff if fix suggested
            suggested_fix = None
            if llm_finding.get("suggested_fix"):
                try:
                    suggested_fix = self.diff_generator.generate_fix_diff(
                        violation,
                        llm_finding.get("code_snippet", ""),
                        llm_finding.get("suggested_fix", ""),
                    )
                except Exception as e:
                    logger.error(f"Failed to generate diff: {e}")

            # Create finding
            finding = Finding(
                id=f"LLM_{file_change.filename}_{idx}",
                rule_id=llm_finding.get("rule_id", f"LLM{idx:03d}"),
                category=category,
                severity=severity,
                title=llm_finding.get("title", "Code Issue"),
                description=llm_finding.get("description", ""),
                explanation=llm_finding.get("explanation", ""),
                violation=violation,
                suggested_fix=suggested_fix,
                suggested_code=llm_finding.get("suggested_fix"),
                metadata={
                    "confidence": llm_finding.get("confidence", 0.0),
                    "llm_generated": True,
                },
            )
            findings.append(finding)

        return findings

    def should_fail_build(self, findings: List[Finding]) -> bool:
        """
        Determine if findings should fail the build.

        Args:
            findings: List of all findings

        Returns:
            True if build should fail
        """
        # Always fail on critical issues
        has_critical = any(f.severity == Severity.CRITICAL for f in findings)
        if has_critical:
            return True

        # In strict mode, fail on warnings too
        if self.strict_mode:
            has_warnings = any(f.severity == Severity.WARNING for f in findings)
            return has_warnings

        return False
