from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, red, green, orange
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import io
from typing import Dict, Any

class PDFGenerator:
    """
    Professional PDF generator for medical claim processing results.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#1e40af'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            textColor=HexColor('#64748b'),
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#1e40af'),
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=HexColor('#e2e8f0'),
            borderPadding=8,
            backColor=HexColor('#f8fafc')
        ))
        
        # Decision style for approved
        self.styles.add(ParagraphStyle(
            name='DecisionApproved',
            parent=self.styles['Normal'],
            fontSize=18,
            spaceAfter=15,
            textColor=HexColor('#16a34a'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            backColor=HexColor('#f0fdf4'),
            borderWidth=1,
            borderColor=HexColor('#16a34a'),
            borderPadding=10
        ))
        
        # Decision style for rejected
        self.styles.add(ParagraphStyle(
            name='DecisionRejected',
            parent=self.styles['Normal'],
            fontSize=18,
            spaceAfter=15,
            textColor=HexColor('#dc2626'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            backColor=HexColor('#fef2f2'),
            borderWidth=1,
            borderColor=HexColor('#dc2626'),
            borderPadding=10
        ))
        
        # Decision style for pending
        self.styles.add(ParagraphStyle(
            name='DecisionPending',
            parent=self.styles['Normal'],
            fontSize=18,
            spaceAfter=15,
            textColor=HexColor('#d97706'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            backColor=HexColor('#fffbeb'),
            borderWidth=1,
            borderColor=HexColor('#d97706'),
            borderPadding=10
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#64748b'),
            alignment=TA_CENTER,
            spaceAfter=10
        ))
    
    def generate_claim_report(self, results: Dict[str, Any]) -> bytes:
        """
        Generate a professional PDF report for claim processing results.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Header
        story.extend(self._create_header())
        
        # Claim Decision Section
        story.extend(self._create_decision_section(results.get('claim_decision', {})))
        
        # Processing Summary
        story.extend(self._create_summary_section(results.get('processing_summary', {})))
        
        # Documents Section
        story.extend(self._create_documents_section(results.get('documents', {})))
        
        # Validation Section
        story.extend(self._create_validation_section(results.get('validation', {})))
        
        # Footer
        story.extend(self._create_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_header(self):
        """Create the PDF header."""
        elements = []
        
        # Title
        title = Paragraph("Claim Processing Result", self.styles['CustomTitle'])
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph("HealthPay AI Engine", self.styles['CustomSubtitle'])
        elements.append(subtitle)
        
        # Generation info
        generation_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        info = Paragraph(f"Generated on {generation_time}", self.styles['InfoText'])
        elements.append(info)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_decision_section(self, decision: Dict[str, Any]):
        """Create the claim decision section."""
        elements = []
        
        # Section header
        header = Paragraph("🎯 CLAIM DECISION", self.styles['SectionHeader'])
        elements.append(header)
        
        # Decision status
        status = decision.get('status', 'unknown').upper()
        if status == 'APPROVED':
            decision_text = f"✅ CLAIM {status}"
            style = self.styles['DecisionApproved']
        elif status == 'REJECTED':
            decision_text = f"❌ CLAIM {status}"
            style = self.styles['DecisionRejected']
        elif status == 'PENDING':
            decision_text = f"⏳ CLAIM {status}"
            style = self.styles['DecisionPending']
        else:
            decision_text = f"❓ CLAIM {status}"
            style = self.styles['DecisionPending']
        
        decision_para = Paragraph(decision_text, style)
        elements.append(decision_para)
        
        # Decision details table
        decision_data = [
            ['Reason:', decision.get('reason', 'No reason provided')],
            ['Confidence Score:', f"{(decision.get('confidence', 0) * 100):.1f}%"],
        ]
        
        if decision.get('recommended_amount'):
            amount = decision['recommended_amount']
            formatted_amount = f"₹{amount:,.2f}" if isinstance(amount, (int, float)) else str(amount)
            decision_data.append(['Recommended Amount:', formatted_amount])
        
        decision_table = Table(decision_data, colWidths=[2*inch, 4*inch])
        decision_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(decision_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_summary_section(self, summary: Dict[str, Any]):
        """Create the processing summary section."""
        elements = []
        
        if not summary:
            return elements
        
        # Section header
        header = Paragraph("📊 PROCESSING SUMMARY", self.styles['SectionHeader'])
        elements.append(header)
        
        # Summary table
        summary_data = []
        if summary.get('total_documents'):
            summary_data.append(['Total Documents Uploaded:', str(summary['total_documents'])])
        if summary.get('classified_documents'):
            summary_data.append(['Documents Classified:', str(summary['classified_documents'])])
        if summary.get('extracted_documents'):
            summary_data.append(['Documents Processed:', str(summary['extracted_documents'])])
        
        if summary_data:
            summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8fafc')),
                ('TEXTCOLOR', (0, 0), (-1, -1), black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_documents_section(self, documents: Dict[str, Any]):
        """Create the documents section."""
        elements = []
        
        if not documents:
            return elements
        
        # Section header
        header = Paragraph("📄 PROCESSED DOCUMENTS", self.styles['SectionHeader'])
        elements.append(header)
        
        for doc_id, doc_info in documents.items():
            # Document type header
            doc_type = doc_info.get('type', 'Unknown').replace('_', ' ').title()
            confidence = doc_info.get('confidence', 0) * 100
            
            doc_header = Paragraph(
                f"<b>{doc_type}</b> (Confidence: {confidence:.1f}%)",
                self.styles['Heading2']
            )
            elements.append(doc_header)
            
            # Document data
            doc_data = doc_info.get('data', {})
            if doc_data:
                data_rows = []
                
                # Common fields mapping
                field_mapping = {
                    'hospital_name': 'Hospital Name',
                    'patient_name': 'Patient Name',
                    'card_holder_name': 'Card Holder Name',
                    'total_amount': 'Total Amount',
                    'sum_insured': 'Sum Insured',
                    'admission_date': 'Admission Date',
                    'discharge_date': 'Discharge Date',
                    'date_of_service': 'Service Date',
                    'diagnosis': 'Diagnosis',
                    'doctor_name': 'Doctor Name',
                    'insurance_company': 'Insurance Company',
                    'policy_number': 'Policy Number',
                    'validity_date': 'Validity Date'
                }
                
                for key, value in doc_data.items():
                    if value and key in field_mapping:
                        display_name = field_mapping[key]
                        if key in ['total_amount', 'sum_insured'] and isinstance(value, (int, float)):
                            display_value = f"₹{value:,.2f}"
                        else:
                            display_value = str(value)
                        data_rows.append([display_name + ':', display_value])
                
                if data_rows:
                    doc_table = Table(data_rows, colWidths=[2*inch, 3*inch])
                    doc_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8fafc')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    
                    elements.append(doc_table)
            
            elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_validation_section(self, validation: Dict[str, Any]):
        """Create the validation section."""
        elements = []
        
        if not validation:
            return elements
        
        # Section header
        header = Paragraph("✅ VALIDATION RESULTS", self.styles['SectionHeader'])
        elements.append(header)
        
        # Check if there are any issues
        missing_docs = validation.get('missing_documents', [])
        discrepancies = validation.get('discrepancies', [])
        warnings = validation.get('warnings', [])
        
        if not missing_docs and not discrepancies and not warnings:
            success_text = Paragraph(
                "✅ All validation checks passed successfully!",
                self.styles['Normal']
            )
            elements.append(success_text)
        else:
            # Missing documents
            if missing_docs:
                missing_header = Paragraph("<b>❌ Missing Documents:</b>", self.styles['Normal'])
                elements.append(missing_header)
                for missing in missing_docs:
                    missing_item = Paragraph(f"• {missing}", self.styles['Normal'])
                    elements.append(missing_item)
                elements.append(Spacer(1, 10))
            
            # Discrepancies
            if discrepancies:
                discrepancy_header = Paragraph("<b>⚠️ Discrepancies Found:</b>", self.styles['Normal'])
                elements.append(discrepancy_header)
                for discrepancy in discrepancies:
                    discrepancy_item = Paragraph(f"• {discrepancy}", self.styles['Normal'])
                    elements.append(discrepancy_item)
                elements.append(Spacer(1, 10))
            
            # Warnings
            if warnings:
                warning_header = Paragraph("<b>⚠️ Warnings:</b>", self.styles['Normal'])
                elements.append(warning_header)
                for warning in warnings:
                    warning_item = Paragraph(f"• {warning}", self.styles['Normal'])
                    elements.append(warning_item)
                elements.append(Spacer(1, 10))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_footer(self):
        """Create the PDF footer."""
        elements = []
        
        elements.append(Spacer(1, 30))
        
        # Separator line
        line_data = [['', '']]
        line_table = Table(line_data, colWidths=[6*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, HexColor('#e2e8f0')),
        ]))
        elements.append(line_table)
        
        elements.append(Spacer(1, 10))
        
        # Footer text
        footer_text = Paragraph(
            "This report was generated by HealthPay AI Engine using advanced machine learning algorithms.<br/>"
            "For questions or concerns, please contact your healthcare provider or insurance company.<br/><br/>"
            "<b>Confidential:</b> This document contains sensitive medical and financial information.",
            self.styles['InfoText']
        )
        elements.append(footer_text)
        
        return elements

