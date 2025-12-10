from typing import List, Dict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class IssueDeduplicator:
    """
    Deduplicate and resolve conflicts in issues
    
    Rules:
    1. Same line, multiple issues → Keep highest severity, mark others as 'superseded'
    2. Same line, conflicting patches → Mark all as 'conflict', require manual review
    
    Severity order: critical > high > medium > low
    """
    
    SEVERITY_ORDER = {
        'critical': 4,
        'high': 3,
        'medium': 2,
        'low': 1
    }
    
    @staticmethod
    def deduplicate_issues(issues: List[Dict]) -> List[Dict]:
        """
        Deduplicate issues and detect conflicts
        
        Returns list of issues with updated status
        """
        # Group issues by file and line
        grouped = defaultdict(list)
        for issue in issues:
            key = (issue['file_path'], issue['line_number'])
            grouped[key].append(issue)
        
        deduplicated = []
        
        for (file_path, line_number), line_issues in grouped.items():
            if len(line_issues) == 1:
                # Single issue on this line - no conflict
                deduplicated.append(line_issues[0])
                continue
            
            # Multiple issues on same line
            logger.info(
                f"Found {len(line_issues)} issues on {file_path}:{line_number}"
            )
            
            # Check for patch conflicts
            has_conflict = IssueDeduplicator._check_patch_conflict(line_issues)
            
            if has_conflict:
                # Mark all as conflict
                conflict_ids = [issue['id'] for issue in line_issues]
                for issue in line_issues:
                    issue['status'] = 'conflict'
                    issue['conflict_with'] = [
                        id for id in conflict_ids if id != issue['id']
                    ]
                    deduplicated.append(issue)
                
                logger.warning(
                    f"Patch conflict detected on {file_path}:{line_number} - "
                    f"requires manual resolution"
                )
            else:
                # No conflict - keep highest severity
                sorted_issues = sorted(
                    line_issues,
                    key=lambda x: IssueDeduplicator.SEVERITY_ORDER.get(
                        x['severity'].value if hasattr(x['severity'], 'value') else x['severity'],
                        0
                    ),
                    reverse=True
                )
                
                # Keep highest severity
                highest = sorted_issues[0]
                deduplicated.append(highest)
                
                # Mark others as superseded
                for issue in sorted_issues[1:]:
                    issue['status'] = 'superseded'
                    issue['superseded_by'] = highest['id']
                    deduplicated.append(issue)
                
                logger.info(
                    f"Deduplication: Kept issue {highest['id']} ({highest['severity']}), "
                    f"superseded {len(sorted_issues) - 1} others"
                )
        
        return deduplicated
    
    @staticmethod
    def _check_patch_conflict(issues: List[Dict]) -> bool:
        """
        Check if issues have conflicting patches
        
        Conflict = multiple issues want to modify the same line with different actions
        """
        actions = set()
        codes = set()
        
        for issue in issues:
            action = issue['action']
            
            # Only replace_line can conflict with other replace_line
            if action == 'replace_line':
                actions.add(action)
                codes.add(issue['code'])
        
        # Conflict if multiple replace_line with different code
        if 'replace_line' in actions and len(codes) > 1:
            return True
        
        # insert_after_line can coexist (multiple insertions)
        # annotate can coexist (multiple comments)
        
        return False
    
    @staticmethod
    def get_conflict_summary(issues: List[Dict]) -> Dict:
        """
        Generate summary of conflicts for UI display
        """
        conflicts = [issue for issue in issues if issue.get('status') == 'conflict']
        
        # Group by file and line
        conflict_groups = defaultdict(list)
        for issue in conflicts:
            key = (issue['file_path'], issue['line_number'])
            conflict_groups[key].append(issue)
        
        summary = {
            'total_conflicts': len(conflict_groups),
            'conflicts': []
        }
        
        for (file_path, line_number), group in conflict_groups.items():
            summary['conflicts'].append({
                'file_path': file_path,
                'line_number': line_number,
                'issue_count': len(group),
                'issue_ids': [issue['id'] for issue in group],
                'actions': [issue['action'] for issue in group],
                'severities': [issue['severity'] for issue in group]
            })
        
        return summary


# Singleton instance
deduplicator = IssueDeduplicator()

