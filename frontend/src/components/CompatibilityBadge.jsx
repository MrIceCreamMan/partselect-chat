import React from 'react';
import './CompatibilityBadge.css';

function CompatibilityBadge({ compatibility }) {
    return (
        <div className={`compatibility-badge ${compatibility.compatible ? 'compatible' : 'not-compatible'}`}>
            <div className="compatibility-icon">
                {compatibility.compatible ? '✓' : '✗'}
            </div>
            <div className="compatibility-details">
                <div className="compatibility-header">
                    <strong>
                        {compatibility.compatible ? 'Compatible' : 'Not Compatible'}
                    </strong>
                </div>
                <div className="compatibility-info">
                    <span>Part: {compatibility.part_number}</span>
                    <span>Model: {compatibility.model_number}</span>
                </div>
                <p className="compatibility-explanation">{compatibility.explanation}</p>
            </div>
        </div>
    );
}

export default CompatibilityBadge;