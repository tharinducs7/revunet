import { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Tag from '@/components/ui/Tag';
import classNames from '@/utils/classNames';
import isLastChild from '@/utils/isLastChild';
import { TbCircleCheck, TbCircleCheckFilled } from 'react-icons/tb';

type RecommendationsProps = {
    data: any[];
};

export const labelClass: Record<string, string> = {
    High: 'bg-red-200 dark:bg-red-200 dark:text-gray-900',
    Medium: 'bg-orange-200 dark:bg-orange-200 dark:text-gray-900',
    Low: 'bg-purple-200 dark:bg-purple-200 dark:text-gray-900',
};

const Recommendations = ({ data }: RecommendationsProps) => {
    const [recommendations, setRecommendations] = useState<any[]>([]);

    useEffect(() => {
        if (recommendations.length === 0) {
            setRecommendations(data);
        }
    }, [data, recommendations.length]);

    const handleToggle = (index: number) => {
        const updatedRecommendations = structuredClone(recommendations).map((rec, idx) => {
            if (idx === index) {
                rec.checked = !rec.checked;
            }
            return rec;
        });
        setRecommendations(updatedRecommendations);
    };

    return (
    
            <div className="mt-4">
                {recommendations.map((recommendation, index) => (
                    <div
                        key={index}
                        className={classNames(
                            'flex items-start justify-between py-4 border-gray-200 dark:border-gray-600',
                            !isLastChild(recommendations, index) && 'border-b',
                        )}
                    >
                        <div className="flex items-start gap-4">
                        <Tag
                                className={`mr-2 rtl:ml-2 ${
                                    recommendation.priority
                                        ? labelClass[recommendation.priority]
                                        : ''
                                }`}
                                style={{ width: "120px"}}
                            >
                                {recommendation.priority}
                            </Tag>
                            <div>
                                <div
                                    className={classNames(
                                        'heading-text font-bold mb-1',
                                        recommendation.checked && 'line-through opacity-50',
                                    )}
                                >
                                    {recommendation.title}
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    {recommendation.recommendation}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
    );
};

export default Recommendations;
