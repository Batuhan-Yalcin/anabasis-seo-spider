import { useParams } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { MonacoDiffViewer } from '@/components/domain/MonacoDiffViewer'
import { useTranslation } from '@/lib/i18n'
import { CheckCircle, XCircle, Edit } from 'lucide-react'

// Mock data - replace with real API call
const mockIssue = {
  id: 15,
  file_path: 'about.php',
  line_number: 156,
  issue_type: 'schema_missing',
  severity: 'critical' as const,
  confidence: 0.92,
  review_required: false,
  reason: 'Product schema eksik, offers.price zorunlu alan',
  original: `<?php
// ... previous code ...

<div class="container">
  <h1>About Us</h1>
  <p>Welcome to our company</p>
</div>

<?php
// ... more code ...
?>`,
  modified: `<?php
// ... previous code ...

<div class="container">
  <h1>About Us</h1>
  <p>Welcome to our company</p>
</div>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{PRODUCT_NAME}}",
  "description": "{{DESCRIPTION}}",
  "offers": {
    "@type": "Offer",
    "price": "{{PRICE}}",
    "priceCurrency": "TRY"
  }
}
</script>

<?php
// ... more code ...
?>`,
}

export function FileDiffViewer() {
  const { projectId, scanId, fileId } = useParams()
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-h1 text-text-primary">
          {mockIssue.file_path} - {t('common.line')} {mockIssue.line_number}
        </h1>
        <p className="mt-2 text-text-secondary">
          {t(`issue.${mockIssue.issue_type}` as any)}
        </p>
      </div>

      {/* Issue details */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Issue Details</CardTitle>
            <div className="flex items-center space-x-2">
              <Badge variant={mockIssue.severity}>
                {t(`severity.${mockIssue.severity}` as any)}
              </Badge>
              <span className="text-sm text-text-secondary">
                {t('common.confidence')}: {(mockIssue.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-text-secondary">{mockIssue.reason}</p>
        </CardContent>
      </Card>

      {/* Diff viewer */}
      <Card>
        <CardHeader>
          <CardTitle>Code Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <MonacoDiffViewer
            original={mockIssue.original}
            modified={mockIssue.modified}
            language="php"
            height="500px"
          />
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex items-center justify-end space-x-4">
        <Button variant="ghost">
          <XCircle className="mr-2 h-4 w-4" />
          {t('action.reject')}
        </Button>
        <Button variant="secondary">
          <Edit className="mr-2 h-4 w-4" />
          {t('action.edit')}
        </Button>
        <Button variant="primary">
          <CheckCircle className="mr-2 h-4 w-4" />
          {t('action.approve')}
        </Button>
      </div>
    </div>
  )
}

